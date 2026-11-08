
import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Initialize production-grade commercial models optimized for low-expense token routing
GLOBAL_EMBEDDINGS = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=1536  # Locks structural dimensions for fast indexing lookups
)

GLOBAL_LLM = ChatOpenAI(
    model="gpt-5-mini", 
    temperature=0.0  # Forces near-deterministic Cypher query generation
)
