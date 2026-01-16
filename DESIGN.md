# Policy Intelligence API - System Design

This document details the architecture and technical design of the RAG-powered Policy Intelligence system.

## 1. High-Level Architecture

The system follows a modular architecture separating concern between data retrieval and AI generation.

```mermaid
graph TD
    subgraph Client_Layer [Client Layer]
        A[External Systems / Postman] -->|HTTP POST JSON| B[FastAPI Router]
    end

    subgraph RAG_Orchestration [RAG Orchestration]
        B --> C[Orchestrator - app/main.py]
        C --> D[Retrieval Pipeline]
        C --> E[Generation Pipeline]
        D -->|Top-K Context| E
    end

    subgraph Retrieval_Pipeline [Retrieval Pipeline]
        D --> D1[Embedding Service]
        D1 -->|all-MiniLM-L6-v2| D2[Vector Search]
        D2 --> D3[(ChromaDB)]
    end

    subgraph Generation_Pipeline [Generation Pipeline]
        E --> E1[Generation Service]
        E1 -->|Phi-2 LLM| E2[Final Analysis]
    end

    subgraph Observability [Observability]
        C --> F[Structured Logs]
        C --> G[Prometheus Metrics]
    end

    %% Styling
    style D3 fill:#f9f,stroke:#333,stroke-width:2px
    style E1 fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#dfd,stroke:#333,stroke-width:1px
```

## 2. Sequence Diagram (Request Flow)

The following diagram illustrates the lifecycle of a single policy search and analysis request.

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI Router
    participant VS as Vector Store
    participant EM as Embedding Model
    participant LLM as Phi-2 Gen Model

    User->>API: POST /search (Claim Description)
    API->>EM: Encode query to Vector
    EM-->>API: 384-dim Vector
    API->>VS: Query Cosine Similarity
    VS->>VS: Search ChromaDB
    VS-->>API: Top-K Relevant Clauses
    
    Note over API, LLM: Start Generation (Augmentation)
    
    API->>LLM: Prompt (Query + Retrieved Context)
    LLM->>LLM: Inference (CPU/GPU)
    LLM-->>API: Generated Analysis
    API->>User: JSON Response (Clauses + Analysis)
```

## 3. Component Breakdown

### 3.1 Retrieval Strategy
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`. Chosen for its balance between inference speed and semantic accuracy.
- **Distance Metric**: **Cosine Similarity**. Used to ensure similarity scores are normalized between 0 and 1, providing better filtering logic for the `min_score` parameter.

### 3.2 Generation Strategy
- **LLM**: `microsoft/phi-2`. A 2.7 billion parameter model that performs exceptionally well on reasoning tasks while remaining small enough for local deployment.
- **Prompt Engineering**: Uses an "Instruct" format to ground the model in the retrieved context, reducing hallucinations by forcing it to cite specific `clause_id`s found in the retrieval step.

### 3.3 Scalability & Performance
- **Async Execution**: The API uses a non-blocking architecture. Since Model Inference (both embedding and generation) is CPU/GPU intensive, these tasks are offloaded to an `asyncio` thread pool executor to keep the event loop responsive for other requests.
- **Local Persistence**: ChromaDB is configured with a persistent path (`./.chromadb`), ensuring data survives application restarts.
