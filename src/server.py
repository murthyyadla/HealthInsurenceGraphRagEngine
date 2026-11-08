import os
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.pipeline import myhealthinsure_pipeline


app = FastAPI(
    title="myHealthInsure Hybrid RAG Engine API",
    description="Production-grade FastAPI gateway orchestrating LangGraph (Neo4j GraphRAG + Chroma VectorRAG)",
    version="2.0.0"
)

# Enable CORS Rules to allow cross-talk connectivity from the React frontend container
from fastapi.middleware.cors import CORSMiddleware

# Initialize app = FastAPI(...) first, then paste this exact configuration block:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows standard GET, POST, OPTIONS requests
    allow_headers=["*"],  # Allows Content-Type and authorization metadata headers
)

# --- 🚀 ADDED CRUCIAL LOGGING MIDDLEWARE FOR YOUR DEFENSE PREPARATION 🚀 ---
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    """
    Catches all hidden uncaught 500 exceptions running mid-execution inside 
    LangGraph or Neo4j driver layers, exposing the true raw stack trace inside the terminal console.
    """
    try:
        return await call_next(request)
    except Exception as e:
        print("\n🚨🚨🚨 === DETECTED CRITICAL PIPELINE CRASH EXCEPTION === 🚨🚨🚨")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\n🔍 DETAILED PYTHON STACK TRACEBACK ERROR LOG:")
        traceback.print_exc()
        print("🚨🚨🚨 === END OF CRASH LOG === 🚨🚨🚨\n")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal Cognitive Engine Crash: {type(e).__name__} - {str(e)}"}
        )
class QueryRequest(BaseModel):
    user_query: str = Field(..., description="The natural language insurance query submitted by the member.")

class QueryResponse(BaseModel):
    user_query: str
    extracted_entities: list[str]
    executed_cypher: str
    routing_path_taken: str
    final_response: str

@app.post("/api/v1/chat")
async def process_insurance_inquiry(request: dict):
    """
    Ingests a raw dictionary dynamically, completely bypassing Pydantic input 
    validation filters to eliminate silent framework gateway drops.
    """
    print(f"\n📥 RECEIVED RAW INCOMING PAYLOAD OVER REST: {request}\n")
    
    # Extract the user text query safely from the dict keys
    user_query = request.get("user_query", "")
    if not user_query:
        return {"final_response": "⚠️ Error: The request payload was empty."}
        
    initial_state = {
        "user_query": user_query,
        "extracted_entities": [],
        "generated_cypher": "",
        "graph_results": [],
        "vector_context": "",
        "final_response": ""
    }
    

    # Run standard LangGraph state machine tracking
    execution_output = myhealthinsure_pipeline.invoke(initial_state)
    
    path_taken = "Graph Ontology Path (Neo4j)"
    if execution_output.get("vector_context") and not execution_output.get("graph_results"):
        path_taken = "Vector Fallback Path (ChromaDB)"
        
    return {
        "user_query": user_query,
        "extracted_entities": execution_output.get("extracted_entities", []),
        "executed_cypher": execution_output.get("generated_cypher", ""),
        "routing_path_taken": path_taken,
        "final_response": execution_output.get("final_response", "Resolution engine stalled.")
    }
        



@app.get("/health")
async def system_health_check():
    return {"status": "healthy", "engine": "LangGraph Active", "api_gateway": "FastAPI Online"}
