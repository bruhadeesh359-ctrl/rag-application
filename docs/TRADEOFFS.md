# Architecture Trade-Offs

Engineering is the application of trade-offs. The following decisions define the RAG Observability Lab.

## 1. BM25 + Dense Retrieval vs. Dense-Only
- **Decision:** Implement Hybrid Retrieval.
- **Reason:** Dense retrieval (vector search) excels at semantic similarity but fails at retrieving highly specific IDs, part numbers, or rare jargon. BM25 excels at exact lexical matching.
- **Trade-off:** Hybrid search increases the storage footprint (maintaining an inverted index alongside a vector database) and increases retrieval latency (running two searches).
- **Future Alternative:** SPLADE or other learned sparse architectures that bake lexical importance into the embedding process natively.

## 2. Reciprocal Rank Fusion (RRF) vs. Learned Fusion
- **Decision:** Combine sparse and dense lists using RRF.
- **Reason:** RRF is a mathematically elegant, parameter-free algorithm that merges ranked lists based solely on rank position.
- **Trade-off:** RRF ignores absolute confidence scores. If BM25 finds a perfect match (score=0.99) and Chroma finds garbage (score=0.1), RRF treats the rank-1 results identically.
- **Future Alternative:** Training a lightweight classifier to weight Dense vs. Sparse scores dynamically based on the query profile.

## 3. Cross-Encoder Reranking vs. Latency
- **Decision:** Re-evaluate the top 20 hybrid results with a Cross-Encoder.
- **Reason:** Bi-encoders (used for indexing) lose massive nuance. Cross-encoders attend to both the query and document simultaneously, achieving vastly superior precision.
- **Trade-off:** Cross-encoders are extremely computationally expensive. They must perform inference at query time for every candidate chunk. This significantly impacts p95 latency.
- **Future Alternative:** Utilizing a fast LLM API (like Gemini Flash) to act as a zero-shot reranker, offloading CPU computation.

## 4. SQLite vs. PostgreSQL
- **Decision:** Local SQLite via `aiosqlite`.
- **Reason:** Simplifies local execution, ensures zero-configuration onboarding, and is perfectly suitable for local observability tracking.
- **Trade-off:** Cannot scale horizontally across multiple instances without file-locking issues.

## 5. Observability Detail vs. Storage Cost
- **Decision:** Capture deep nested spans (retrieval, contextualization, LLM, validation) and trace inputs/outputs.
- **Reason:** Total visibility is required to isolate RAG failures (e.g., did it fail because retrieval missed the document, or because the LLM hallucinated?).
- **Trade-off:** Storing full contexts and LLM outputs in spans drastically increases database size over time.
