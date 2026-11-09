import os
from typing import TypedDict, List, Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_chroma import Chroma
from neo4j import GraphDatabase
from langgraph.graph import StateGraph, START, END
from src.config import GLOBAL_EMBEDDINGS, GLOBAL_LLM

class HybridGraphState(TypedDict):
    user_query: str
    extracted_entities: List[str]
    generated_cypher: str
    graph_results: List[Dict[str, Any]]
    vector_context: str
    final_response: str

class AnthemSBCStructuredTerms(BaseModel):
    extracted_symptoms: List[str] = Field(description="Clinical symptoms or conditions mentioned.")
    standard_sbc_benefits: List[str] = Field(description="SBC terms like 'Specialist visit' or 'Imaging'.")

    

def extraction_node(state: HybridGraphState) -> Dict[str, Any]:
    llm =     GLOBAL_LLM.with_structured_output(AnthemSBCStructuredTerms)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Analyze user queries and extract clinical terms, mapping them to standard SBC categories."),
        ("human", "{user_query}")
    ])
    parsed = (prompt | llm).invoke({"user_query": state["user_query"]})
    return {"extracted_entities": parsed.extracted_symptoms + parsed.standard_sbc_benefits}

def cypher_generation_node(state: HybridGraphState) -> Dict[str, Any]:
    if not state["extracted_entities"]:
        return {"generated_cypher": ""}
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "Task: Generate a raw Cypher statement to query a health insurance graph.\n"
            "Schema Layout:\n"
            "- FHIR_Condition (Properties: fhir_id, icd10_code, display_name)\n"
            "- FHIR_Procedure (Properties: fhir_id, cpt_code, display_name)\n"
            "- HL7_CoverageRule (Properties: rule_id, requirement, copay)\n"
            "Relationships:\n"
            "(:FHIR_Condition)-[:INDICATES_PROCEDURE]->(:FHIR_Procedure)-[:GOVERNED_BY_RULE]->(:HL7_CoverageRule)\n\n"
            "Instructions:\n"
            "Create a query matching terms: {entities} dynamically using CONTAINS operations.\n"
            "Return everything as key value attributes. Output ONLY raw code text without markdown ticks."
        )),
        ("human", "Build query for: {user_query}")
    ])
    res = (prompt | GLOBAL_LLM).invoke({"entities": state["extracted_entities"], "user_query": state["user_query"]})
    raw_content = ""
    if isinstance(res.content, list):
        for part in res.content:
            if isinstance(part, str):
                raw_content += part
            elif isinstance(part, dict) and "text" in part:
                raw_content += part["text"]
    else:
        raw_content = str(res.content)

    clean_cypher = res.content.replace("```cypher", "").replace("```", "").strip()
    return {"generated_cypher": clean_cypher}

def execute_neo4j_node(state: HybridGraphState) -> Dict[str, Any]:
    if not state["generated_cypher"]:
        return {"graph_results": []}
    
    records = []
    try:
        # Inject explicit timeout parameters to prevent infinite connection hangs
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://host.docker.internal:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password")),
            connection_timeout=3.0,     # Max 3 seconds to establish socket bridge
            max_transaction_retry_time=2.0 # Abandon hanging query transactions quickly
        )
        with driver.session() as session:
            result = session.run(state["generated_cypher"])
            for record in result:
                records.append(record.data())
        driver.close()
    except Exception as e:
        print(f"⚠️ Neo4j connection stalled or timed out: {str(e)}")
        records = [{"error": "timeout"}] # Forces the conditional router to drop to Vector Fallback instantly
        
    return {"graph_results": records}




def vector_fallback_node(state: HybridGraphState) -> Dict[str, Any]:
    """
    Node 4: Fast Fallback Track. Utilizes a pre-indexed local Chroma vector database
    to extract matching legal text snippets. 
    """
    print("⚠️ Neo4j Ontology missed. Traversing local text vector index...")
    
    # Establish absolute path targeting the database volume directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "database")
    
    context_str = "No backup policy parameters resolved."
    
    try:
        # Check if the database index actually exists before opening the disk socket
        if os.path.exists(db_path) and len(os.listdir(db_path)) > 0:
            
            # Open the existing storage vector index instantly without rebuilding it
            db = Chroma(persist_directory=db_path, embedding_function=GLOBAL_EMBEDDINGS)
            
            # Limit the search kwargs to pull context parameters immediately
            docs = db.as_retriever(search_kwargs={"k": 2}).invoke(state["user_query"])

            context_str = "\n".join([doc.page_content for doc in docs])
        else:
            print("⚠️ Local database index directory is empty. Ensure ingest_pdf.py ran completely.")
    except Exception as e:
        print(f"❌ Vector fallback layer fault: {str(e)}")
        context_str = f"Vector index read fault: {str(e)}"
        
    return {"vector_context": context_str}


def graph_synthesis_node(state: HybridGraphState) -> Dict[str, Any]:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a myHealthInsure Agent. Generate a definitive answer using the following structured graph data records."),
        ("human", "User: {user_query}\n\nGraph Payload:\n{graph_results}")
    ])
    res = (prompt | GLOBAL_LLM).invoke({"user_query": state["user_query"], "graph_results": state["graph_results"]})
    return {"final_response": res.content}

def vector_synthesis_node(state: HybridGraphState) -> Dict[str, Any]:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a myHealthInsure Agent. The structured graph failed, so compile an answer using this backup unstructured handbook context."),
        ("human", "User: {user_query}\n\nVector Context:\n{vector_context}")
    ])
    res = (prompt | GLOBAL_LLM).invoke({"user_query": state["user_query"], "vector_context": state["vector_context"]})
    return {"final_response": res.content}

def route_neo4j_evaluation(state: HybridGraphState) -> str:
    results = state["graph_results"]
    if not results or "error" in results:
        return "fallback_path"
    return "graph_path"

workflow = StateGraph(HybridGraphState)
workflow.add_node("extract", extraction_node)
workflow.add_node("generate_cypher", cypher_generation_node)
workflow.add_node("execute_neo4j", execute_neo4j_node)
workflow.add_node("vector_fallback", vector_fallback_node)
workflow.add_node("synthesize_graph", graph_synthesis_node)
workflow.add_node("synthesize_vector", vector_synthesis_node)

workflow.add_edge(START, "extract")
workflow.add_edge("extract", "generate_cypher")
workflow.add_edge("generate_cypher", "execute_neo4j")

workflow.add_conditional_edges(
    "execute_neo4j",
    route_neo4j_evaluation,
    {"graph_path": "synthesize_graph", "fallback_path": "vector_fallback"}
)
workflow.add_edge("vector_fallback", "synthesize_vector")
workflow.add_edge("synthesize_graph", END)
workflow.add_edge("synthesize_vector", END)

myhealthinsure_pipeline = workflow.compile()
