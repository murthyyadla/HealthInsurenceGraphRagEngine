import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from dotenv import load_dotenv
load_dotenv() 


LOCAL_PDF_PATH = "data/BenefitSummary.pdf"
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")

def index_local_pdf():
    # Structural check to safeguard execution parameters
    if not os.path.exists(LOCAL_PDF_PATH):
        print(f"\n🚨 Error: No file found at '{LOCAL_PDF_PATH}'.")
        print("👉 Action Required: Open your browser, download any Summary of Benefits (SBC) PDF,")
        print(f"   rename it exactly to 'health_benefit_summary.pdf', and drop it inside your 'data/' folder first!\n")
        return

    print("Parsing multi-page tabular document grids from local storage...")
    loader = PyPDFLoader(LOCAL_PDF_PATH)
    raw_pages = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    processed_chunks = text_splitter.split_documents(raw_pages)

    print(f"🌱 Seeding ChromaDB with local HuggingFace embeddings (all-MiniLM-L6-v2)...")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536)
    
    # Clean up old corrupted database directories dynamically on disk
    if os.path.exists(DB_DIR):
        import shutil
        shutil.rmtree(DB_DIR)
        
    Chroma.from_documents(
        documents=processed_chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    print("✨ Clean vector database initialized successfully from local PDF file!")

if __name__ == "__main__":
    index_local_pdf()


