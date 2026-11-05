import os
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

PDF_URL = "https://anthem.com"
LOCAL_PDF_PATH = "data/BenefitSummary.pdf"
DB_DIR = "database"

def download_and_index_real_pdf():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(LOCAL_PDF_PATH):
        print(f"📡 Downloading official 2026 SBC document blueprint from remote server...")
        response = requests.get(PDF_URL, headers={"User-Agent": "Mozilla/5.0"})
        with open(LOCAL_PDF_PATH, "wb") as f:
            f.write(response.content)
        print("💾 File saved locally.")

    print("Parsing multi-page tabular document grids...")
    loader = PyPDFLoader(LOCAL_PDF_PATH)
    raw_pages = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    processed_chunks = text_splitter.split_documents(raw_pages)

    print(f"🌱 Seeding ChromaDB Vector Indices with {len(processed_chunks)} real text chunks...")
    Chroma.from_documents(
        documents=processed_chunks,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory=DB_DIR
    )
    print("✨ Vector database initialized successfully!")

if __name__ == "__main__":
    download_and_index_real_pdf()
