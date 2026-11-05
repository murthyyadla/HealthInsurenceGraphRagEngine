import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.pipeline import myhealthinsure_pipeline

app = FastAPI(
    title="myHealthInsure Hybrid RAG Engine API",
    description="Production-grade FastAPI gateway orchestrating LangGraph (Neo4j GraphRAG + Chroma VectorRAG)",
    version="2.0.0"
)

# Enable CORS Rules to allow cross-talk connectivity from the React frontend container
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    user_query: str = Field(..., description="The natural language insurance query submitted by the member.")

class QueryResponse(BaseModel):
    user_query: str
    extracted_entities: list[str]
    executed_cypher: str
    routing_path_taken: str
    final_response: str

@app.post("/api/v1/chat", response_model=QueryResponse, summary="Process a health insurance benefit inquiry")
async def process_insurance_inquiry(request: QueryRequest):
    initial_state = {
        "user_query": request.user_query,
        "extracted_entities": [],
        "generated_cypher": "",
        "graph_results": [],
        "vector_context": "",
        "final_response": ""
    }
    try:
        execution_output = myhealthinsure_pipeline.invoke(initial_state)
        path_taken = "Graph Ontology Path (Neo4j)"
        if execution_output.get("vector_context") and not execution_output.get("graph_results"):
            path_taken = "Vector Fallback Path (ChromaDB)"
            
        return QueryResponse(
            user_query=execution_output["user_query"],
            extracted_entities=execution_output["extracted_entities"],
            executed_cypher=execution_output["generated_cypher"],
            routing_path_taken=path_taken,
            final_response=execution_output["final_response"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Processing Exception: {str(e)}")

@app.get("/health")
async def system_health_check():
    return {"status": "healthy", "engine": "LangGraph Active", "api_gateway": "FastAPI Online"}
