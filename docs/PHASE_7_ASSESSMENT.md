# Phase 7 Assessment

## 1. Existing Backend Architecture
Currently, the FastAPI application (`app/main.py`) acts as a basic entry point that includes multiple disjoint routers:
- `api_router` (`app/api/endpoints.py`): Contains ingestion, retrieval, RAG, and health endpoints. Prefix: `/api/v1`
- `eval_router` (`app/api/evaluation.py`): Contains evaluation endpoints. Prefix: `/api/evaluation`
- `obs_router` (`app/api/observability.py`): Contains observability endpoints. Prefix: `/api` (meaning endpoints become `/api/observability/...`)

## 2. Existing Services and Components
The existing project contains a highly developed set of ML and business logic services across `app/services`:
- `chunker.py`, `document_parser.py`: Ingestion logic
- `sparse_index.py`, `vector_store.py`, `sqlite_storage.py`: Storage implementations
- `retrievers.py`, `hybrid_retriever.py`, `embeddings.py`, `fusion.py`, `reranker.py`: Retrieval implementations
- `context_builder.py`, `generator.py`, `citation_validator.py`, `groundedness.py`, `grounding.py`, `llm_provider.py`: LLM/Generation logic
- `rag_service.py`: Central orchestrator of the entire RAG pipeline
- `metrics.py`: Metrics for evaluation
- `app/core/tracer.py`: Thread-safe distributed tracing via contextvars

## 3. Dependency Injection Issues
Currently, `app/api/endpoints.py` statically initializes services globally at import time:
```python
relational_storage = SQLiteStorage()
vector_storage = ChromaVectorStorage()
sparse_index = BM25SparseIndex()
embedding_service = EmbeddingService()
dense_retriever = DenseRetriever(vector_storage, embedding_service, relational_storage)
sparse_retriever = SparseRetriever(sparse_index, relational_storage)
# ... etc ...
rag_service = RAGService(hybrid_retriever)
```
This prevents proper lifecycle management, makes mocking difficult, and forces models to load immediately upon startup.

## 4. API Schema Coverage
There is a lack of comprehensive Pydantic request/response models. `RetrievalRequest` is present, but responses are often just raw dictionaries or internal Python objects returned from services. There are no standardized error formats or metadata envelopes.

## 5. Architectural Inconsistencies and Missing APIs
- **Versioning**: Not all endpoints are consistently versioned (eval and observability use different prefixing).
- **Health/System**: `endpoints.py` lacks a dedicated `/system` route returning hardware, model, and OS context.
- **Ingestion**: `/documents/ingest` is merely a placeholder that doesn't trigger the real `document_parser` and `chunker`.
- **Retrieval metadata**: Responses lack `trace_id` injection from the observability framework.
- **Trace Propagation**: Request and trace correlation IDs aren't established at the FastAPI middleware layer or passed explicitly.
- **Folder Structure**: Needs reorganization into `api/v1/...` routers, rather than monolithic files.

## 6. Implementation Plan
To fulfill the Phase 7 production backend requirements without modifying underlying services, I will:

1. **Restructure Directory Layout**:
   - `app/api/v1/` containing focused routers: `health.py`, `system.py`, `ingestion.py`, `retrieval.py`, `rag.py`, `evaluation.py`, `observability.py`, `experiments.py`.
   - `app/api/dependencies.py` to handle DI.
   - `app/api/router.py` to aggregate the V1 routers.
   
2. **Refactor Dependency Injection**:
   - Create dependencies (e.g., `get_rag_service`, `get_storage`) to initialize and cache services at runtime or application lifespan, eliminating global scope initializations.
   
3. **Pydantic Contracts**:
   - Create `app/schemas/api/` schemas for strongly typed Requests and Responses. Standardize error responses (400, 422, 500) and generic success envelopes.
   
4. **Middleware for Observability & Correlation**:
   - Introduce a middleware that establishes `request_id` and integrates with `TraceManager` to ensure all API errors and traces correctly capture API-level exceptions and metadata.

5. **Clean Router Integration**:
   - Rewrite endpoints to cleanly validate input schemas, call injected services, and map service results to strict API response schemas.

6. **Documentation and Tests**:
   - Generate Swagger/OpenAPI docs for all schemas.
   - Write unit tests in `tests/api/v1/` mocking the injected dependencies to ensure API contracts behave perfectly without hitting models.
