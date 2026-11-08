# HealthInsurenceBenefitsAgent: Forward Deployment Engineering & Infrastructure Integration

HealthInsurenceBenefitsAgent is a containerized full-stack platform designed to parse complex, unstructured health insurance policy data and model it into an enterprise-ready Neo4j knowledge graph. This repository serves as a blueprint for Forward Deployment Engineers (FDEs) managing rapid, reliable client-side rollouts—featuring hardened container networking, automated environment initialization, and seamless cross-service integrations.

## 🏗️ System Integration Architecture

The application environment mirrors an enterprise client-side setup, engineered via **Docker Compose** to manage hardened container isolation, local volume lifecycles, and environment synchronization.

*   **Integration Backend:** FastAPI (Python) serving as the core API gateway and AI agent orchestrator (OpenAI integration).
*   **Enterprise Storage Layer:** Neo4j (Graph Database) for mapping intricate, multi-layered healthcare coverages and client ontologies.
*   **User/Analyst Interface:** React frontend containerized and served using Nginx for high-availability UI delivery.
*   **Environment Management:** Deterministic configuration parsing utilizing `.env` mapping directly into internal container runtimes.

## 🛠️ Forward Deployment Engineering Highlights

*   **Production Network Debugging:** Diagnosed and corrected critical container-to-host connection dropouts and socket connection refusals (`Errno 111`). Migrated from fragile `host.docker.internal` host-gateways to explicit internal Docker bridge networking to guarantee deterministic internal service discovery (`bolt://neo4j-db:7687`).
*   **Robust Client Provisioning:** Mitigated container start-up race conditions by configuring rigorous `depends_on` chains, ensuring database services are fully listening before launching dependent API configurations.
*   **State & Cache Invalidation Utilities:** Programmed a secure environment purge script capable of blowing away corrupted database volumes, local caching layers, and dead docker nodes to guarantee clean deployment baselines in volatile test fields.

## 🚀 Client-Side Cluster Initialization (Clean Boot)

To resolve unhandled environment collisions, security lockouts, or corrupt local database states, trigger a complete deployment refresh:

```bash
# 1. Stop all active client nodes and unmount corrupted volumes
docker compose down -v

# 2. Prune old engine caching layers to force clean image builds
docker builder prune -f

# 3. Spin up and build the environment stack in daemon mode
docker compose up -d --build

```
                System Architecture

1. Data Ingestion 


===========================================================================================
                    HYBRID GraphRAG & VECTOR DB DATA INGESTION PIPELINE
===========================================================================================

 [ RAW UNSTRUCTURED DATA ] ──► (PDF / Policy Documents / Unstructured Text)
                                       │
                                       ▼ 
 ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
 │ STEP 1: PRE-PROCESSING & TEXT CHUNKING                                                       │
 │ - Document Cleansing & Normalization                                                         │
 │ - Sliding-Window Chunking (e.g., 500-token chunks with 100-token overlap)                     │
 └─────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                       │
                                       ▼ Iterates per chunk via LangGraph State Channels
 ================================================================================================
      [ LANGGRAPH CORE AGENTIC ORCHESTRATION PIPELINE ]
 ================================================================================================
                                       │
                                       ├──► Stream Payload into Central State
                                       ▼
 ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
 │ STEP 2: PARSING TIER (LLM INTERACTION 1 - STRUCTURED GENERATION)                             │
 │ - LLM extracts core Entities (Policies, Constraints, Rules, Medical Codes)                    │
 │ - LLM maps directional Relationships (COVERS, EXCLUDES, DEPENDS_ON)                          │
 │ - Output formatted as strict JSON Schema Object                                              │
 └─────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                       │
                                       ▼ Passes to Validation Guard Node
 ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
 │ STEP 3: STRUCTURAL & ONTOLOGY VALIDATION GATE                                                │
 │ - Programmatic schema verification against strict Neo4j database constraints                 │
 │ - PASS ──► Advance to Bifurcated Ingest Split                                               │
 │ - FAIL ──► Loop back to Repair Agent with Compiler Error Metadata                            │
 └─────────────────────────────────────┬────────────────────────────────────────────────────────┘
                                       │
                                       ▼ [ BIFURCATED STORAGE PIPELINE EXECUTION ]
                    ───────────────────┴───────────────────
                   │                                       │
                   ▼                                       ▼
 ┌───────────────────────────────────┐   ┌───────────────────────────────────┐
 │ STEP 4A: SEMANTIC VECTOR ROUTE    │   │ STEP 4B: RELATIONAL GRAPH ROUTE   │
 │ (LLM Interaction 2: Embedding Engine)│   │ (Deterministic Cypher Generation) │
 │                                   │   │                                   │
 │ - Raw text chunk routed to        │   │ - Map validated entities/links to │
 │   text-embedding-3-small          │   │   idempotent Cypher operations    │
 │ - Generates 1536-dim vector float │   │ - Formulate write batch using     │
 │ - Writes to Vector DB Cluster     │   │   MERGE and ON CREATE SET clauses │
 └─────────────────┬─────────────────┘   └─────────────────┬─────────────────┘
                   │                                       │
                   ▼ [ PERSISTENCE TIER ]                  ▼ [ PERSISTENCE TIER ]
         ┌───────────────────┐                   ┌───────────────────┐
         │  Vector Database  │                   │Neo4j Knowledge Graph│
         │ (Chroma/Qdrant)   │                   │ (Discrete Schema) │
         └─────────┬─────────┘                   └─────────┬─────────┘
                   │                                       │
                   └───────────────────┬───────────────────┘
                                       │
                                       ▼ Atomic Sync Anchor (Linked via Chunk_ID)
 ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
 │ STEP 5: OUT-OF-BAND EVALUATION & MONITORING (LLM INTERACTION 3 - CRITIC)                     │
 │ - Compute Retrieval-Augmented metrics (Faithfulness, Completeness, Hallucination-check)       │
 │ - Emit batch logs and asynchronous OpenTelemetry traces to LangSmith / OpenInference         │
 └──────────────────────────────────────────────────────────────────────────────────────────────┘
===========================================================================================

1. Document Extraction & Token Chunking: Unstructured medical policies are parsed into text strings. The pipeline slices the document into dense semantic fragments with overlapping buffers to avoid breaking a sentence or a coverage rule across boundaries. Every chunk is stamped with an immutable global tracking identity (Chunk_ID).
2. Entity & Relationship Graph Extraction (LLM-Driven): The text chunk is fed into an LLM using structured extraction prompts. The model identifies the primary components (e.g., (:UserGroup), (:MedicalProcedure), (:InsurancePolicy)) and maps the relational links between them.
3. The Orchestration Fork (Bifurcation): This is the core engineering design. LangGraph splits the clean state into two distinct target actions:
    • The Dense Vector Stream: The raw text fragment is converted into an embedding using an embedding engine and stored in the Vector Database, indexed under the corresponding Chunk_ID.
    • The Relational Graph Stream: The JSON metadata structure is mapped directly into an optimized Cypher transactional payload and executed against Neo4j, injecting the real-world semantic data rules and creating links keyed back to that same Chunk_ID.
4. Hybrid Sync (Cross-Database Indexing Keys): By storing the identical Chunk_ID as a property in Neo4j and as metadata inside the Vector DB, the pipeline achieves an atomic cross-database bridge. During an application search runtime, a user query can match context chunks in the vector space and seamlessly pull structural relation lines from Neo4j in sub-milliseconds.
5. Observability Isolation Gating: The pipeline closes by pushing complete graph tracing metrics out-of-band to LangSmith. This allows Forward Deployment Engineers to audit the performance footprint of individual agent blocks and measure embedding latency across production runtimes.


Agent :

===========================================================================================
                            SYSTEM ARCHITECTURE  (AGENTIC AI)
===========================================================================================

     [ PUBLIC INTERNET / BROWSER TIER ]
                     │
                     │  HTTP / HTTPS (Port 3000)
                     ▼
  ┌──────────────────────────────────────┐
  │         React UI Web Client          │ ── Served via optimized Nginx container
  └──────────────────────────────────────┘
                     │
                     │  REST API Calls / JSON Payload (Port 8000)
                     ▼
===========================================================================================
     [ ISOLATED DOCKER CONTAINER NETWORK (myhealthinsure_network) ]
===========================================================================================
                     │
                     ▼
  ┌──────────────────────────────────────┐
  │     FastAPI Ingestion Gateway        │ ── State Broker & REST Endpoint Router
  └──────────────────┬───────────────────┘
                     │
                     ▼
  ┌──────────────────────────────────────┐     ┌───────────────────────────────────┐
  │      LangGraph Orchestrator          │ ───►│  Observability & Evaluation Stack │
  │  (Stateful Agent Loops & Reducers)  │     │  (LangSmith / OpenInference Trace)│
  └──────────────────┬───────────────────┘     └───────────────────────────────────┘
                     │
                     │  Internal DNS Route: bolt://neo4j-db:7687
                     │  (Binary Bolt Protocol - TCP Handshake)
                     ▼
  ┌──────────────────────────────────────┐
  │     Neo4j Graph Database Cluster     │ ── OLTP Graph Storage & Knowledge Ontology
  └──────────────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Persistent Volumes   │ ── Mount Paths:
         │  ├─ neo4j_data        │    - /data (Graph store file system)
         │  └─ neo4j_logs        │    - /logs (Query engine logs)
         └───────────────────────┘
===========================================================================================




            Hybrid Agentic GraphRAG Blueprint

Step 1: Public Internet / Browser Tier (Ingress)

• The Ingress Entrypoint: Public client traffic or browser-based user interactions trigger the initial system request.
• The Presentation Endpoint: This payload communicates over standard web protocols (HTTP / HTTPS) on external Port 3000 to land directly on the React UI Web Client. The application interface assets are served using a highly optimized, high-availability Nginx container.

Step 2: Gateway Border & Boundary Traversal

• The Cross-Tier Transport: The React container translates frontend events into structured REST API Calls / JSON Payloads, dispatching them down to the application gateway.
• The Network Boundary Entry: This traffic enters via Port 8000, passing out of the public internet tier to cross into the Isolated Docker Container Network (myhealthinsure_network). This private network completely isolates the internal backend and storage operations from direct external access.

Step 3: Application Core & Gateway Management

• The Request Broker: The traffic hits the FastAPI Ingestion Gateway. FastAPI acts as the centralized system State Broker and REST Endpoint Router, managing container life cycles and routing incoming requests into the internal compute layers.
• The Orchestration Hand-off: FastAPI directly instantiates and forwards the compute payload to the LangGraph Orchestrator, which manages the underlying execution state.

Step 4: Stateful Logic & Telemetry Bifurcation

• The Agentic Coordination Hub: The LangGraph Orchestrator acts as the central execution brain. It handles Stateful Agent Loops & Reducers, managing short-term transaction memories and data-cleansing operations.
• The Out-of-Band Tracing Hook: Before splitting data to the storage engines, LangGraph emits asynchronous, non-blocking trace payloads horizontally to the Observability & Evaluation Stack. Systems metrics, token costs, and agent runtimes are ingested by LangSmith / OpenInference Traces without delaying the live application path.

Step 5: Dual-Engine Hybrid Storage Tier Execution

• The Workload Bifurcation: LangGraph executes a synchronized split to send data into the Dual-Engine Hybrid Storage Layer, optimizing data for two fundamentally different query patterns:
	1. The Unstructured Vector Path: The engine streams text fragments down to the Vector Database, handling semantic text matching, indexing, and high-dimensional floating-point embeddings.
	2. The Structured Graph Path: Concurrently, the engine translates relational metadata schemas into optimized Cypher mutations, piping them directly to the Neo4j Graph Database to build and enforce strict structural data lineages, constraints, and nodes.

Step 6: Hardware Persistence Tier (Egress)

• The Cross-Database Merger: Both independent storage streams converge their finalized transaction logs onto a unified physical layout.
• The Host File System Binding: The database engines write data out of volatile container memory down to physical Persistent Volumes. This host data mount tier maps files directly to physical disks, guaranteeing that the underlying graph topology and semantic vector indexes survive total cluster power losses, reboots, or container updates.





