# Test Matrix

The RAG Observability Lab enforces testing across multiple distinct categories to verify functionality objectively.

## 1. Unit Tests
- **Target:** Isolated functions, components, and core utilities.
- **Command:** `pytest tests/` (Backend)
- **Focus:** 
  - Token counting logic
  - Chunking overlap boundaries
  - RRF fusion mathematical correctness
  - OpenTelemetry context propagation

## 2. Integration Tests
- **Target:** Data pathways involving multiple components (e.g., Ingestion -> Vector Store).
- **Command:** `pytest tests/test_integration.py`
- **Focus:**
  - Mocked endpoints routing correctly to the Hybrid Retriever.
  - Ensuring tracing middleware captures both 200s and 500s.
  - Validating ChromaDB index insertion mechanisms.

## 3. Evaluation Benchmark Tests
- **Target:** Offline measuring of pipeline recall and groundedness accuracy.
- **Command:** Requires explicit evaluation dataset (Not automatically executed in CI).
- **Focus:**
  - Recall@5, MRR, NDCG of the `all-MiniLM-L6-v2` dense embeddings.
  - Groundedness LLM-as-a-judge accuracy.

## 4. Frontend Compilation & Linting
- **Target:** Ensuring the React SPA builds correctly and is type-safe.
- **Command:** `cd frontend && npm ci && npm run lint && npm run build`
- **Focus:**
  - React Hooks dependency arrays (via `oxlint`).
  - TypeScript strict type compliance (`tsc -b`).

## 5. Docker Validation (CI)
- **Target:** Ensuring container reproducibility.
- **Command:** `docker compose build`
- **Focus:**
  - Preventing broken dependencies from passing CI.
  - Ensuring the `.dockerignore` effectively protects the build context.

## 6. End-to-End Smoke Test
- **Target:** Complete RAG flow starting from a local server.
- **Command:** Triggered manually post-deployment.
- **Expected Behavior:** An uploaded document is successfully parsed, chunked, and stored. A subsequent query successfully triggers sparse + dense retrieval, reciprocal rank fusion, cross-encoder reranking, context building, LLM generation, citation validation, and trace logging.
