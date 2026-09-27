# RAG Observability Lab API (v1)

## Base URL
`/api/v1`

## Common Schemas

### APIResponse
Every endpoint returns data wrapped in a common schema:
```json
{
  "request_id": "uuid",
  "data": { ... },
  "meta": { ... } // Optional
}
```

### PaginatedResponse
```json
{
  "request_id": "uuid",
  "data": [ ... ],
  "meta": {
    "page": 1,
    "page_size": 50,
    "total": 100
  }
}
```

## Endpoints

### 1. System & Health
* `GET /health` - Liveness probe.
* `GET /system` - Readiness probe. Exposes loaded models and runtime capabilities.

### 2. Ingestion
* `POST /ingest` 
  * `multipart/form-data`: `file`
  * Parses, chunks, embeds, and stores a document in vector and relational storage.

### 3. Retrieval
* `POST /retrieve/bm25` - Sparse retrieval
* `POST /retrieve/dense` - Dense vector retrieval
* `POST /retrieve/hybrid` - Hybrid (RRF) + Cross-Encoder reranking
  * **Payload:** `{"query": "string", "top_k": int}`

### 4. RAG & Generation
* `POST /rag/query` - Full E2E RAG generation with LLM and Observability tracking.
  * **Payload:** `{"query": "string", "experiment_id": "optional_string", "include_debug": bool}`
* `POST /rag/inspect` - Retrieve contexts with intermediate inspection data (rankings, fusion scores).

### 5. Observability
* `GET /observability/traces` - List tracing telemetry.
* `GET /observability/traces/{trace_id}` - Get full trace, including spans and errors.
* `GET /observability/summary` - Aggregate latency and success rate telemetry.

### 6. Evaluation
* `POST /evaluation/run` - Trigger an async evaluation job.
  * **Payload:** `{"dataset_path": "string", "experiment_id": "string", "retriever": "hybrid_rerank"}`
* `GET /evaluation/runs` - List past experiments.
* `GET /evaluation/runs/{experiment_id}` - Get metrics for a specific experiment (Recall, MRR, NDCG).
