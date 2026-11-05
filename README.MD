# HealthInsure Hybrid GraphRAG + VectorRAG Pipeline

An enterprise-grade, production-quality health insurance care navigation microservice. This application leverages **LangGraph** to coordinate deterministic traversals across a **Neo4j FHIR Ontology Graph** with automatic fallbacks to a **ChromaDB Vector Store** when parsing unstructured 2026 Summary of Benefits and Coverage (SBC) PDFs.

## 🚀 Key Architectural Features
- **Ontological Grounding:** Anchors user inquiries directly to official clinical taxonomies (**ICD-10-CM**, **CPT**, and **HL7 ActCode**).
- **Asynchronous Cognitive Orchestration:** Replaces black-box agent loops with predictable, graph-based node execution states via **LangGraph**.
- **Resilient Fallback Interceptor:** Programmatically shifts execution routes to Vector similarity searches if a graph search misses, completely eliminating missing data crashes.
- **Enterprise-Grade Infrastructure:** Fully decoupled **FastAPI backend microservice gateway** completely containerized within a **Docker and Docker Compose stack**.

## 🛠️ Local Environment Boot Sequence

### 1. Initialize and Seed Databases
```bash
# Export your orchestration secrets
export OPENAI_API_KEY="your-api-key-here"

# Seed the Neo4j Graph Ontologies
python src/seed_graph.py

# Ingest and vector-index real multi-page 2026 SBC PDFs
python src/ingest_pdf.py
```

### 2. Launch Container Infrastructure via Docker
```bash
docker-compose up --build
```
Once your build is complete, access your interactive web dashboard playground at:
👉 **`http://localhost:3000`**
