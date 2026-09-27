# Phase 3 Assessment

## Current Phase 2 Architecture
Phase 2 established a rigid foundation for chunking, embedding, and single-strategy retrieval:
- **Chunking**: `FixedSizeChunker` handles exact token boundaries and overlap, emitting strict `Chunk` objects.
- **Provenance**: `Provenance` objects trace every chunk back to its source document, file, and page.
- **Embeddings**: `EmbeddingService` manages CPU/CUDA fallback for `sentence-transformers/all-MiniLM-L6-v2`.
- **Storage**: `SQLiteStorage` handles relational metadata, `ChromaVectorStorage` handles dense vectors, and `BM25SparseIndex` handles sparse inverted indexes.
- **Retrievers**: `DenseRetriever` and `SparseRetriever` are completely decoupled, both independently executing searches and returning identical `RetrievedChunk` structures containing `original_rank` and `score`.

## Reusable Components
- **Data Models**: `DocumentCreate`, `ChunkCreate`, `Chunk`, `Provenance`, `RetrievedChunk`.
- **Storage Interfaces**: `RelationalStorage`, `VectorStorage`, `SparseIndex`.
- **Retrieval Interfaces**: The unified return types from Phase 2 make fusion straightforward.
- **Observability Hooks**: Basic timing logs are present but need expansion in the Hybrid retriever.

## Phase 3 Implementation Plan
1. **Reciprocal Rank Fusion (RRF)**: Implement an isolated, testable `RRFFusion` class that takes lists of `RetrievedChunk` and applies the RRF formula: $1 / (k + rank)$.
2. **Hybrid Retriever**: Implement `HybridRetriever` to orchestrate parallel calls to `DenseRetriever` and `SparseRetriever`, apply RRF, and return the fused `Candidate Set`.
3. **Cross-Encoder Reranker**: Implement `CrossEncoderReranker` using `cross-encoder/ms-marco-MiniLM-L-6-v2` with strict batching and CPU/CUDA awareness to respect the 6GB VRAM constraint.
4. **Final Pipeline**: Update `HybridRetriever` to execute the reranker on the fused candidates.
5. **Retrieval Inspector**: Add `POST /api/v1/retrieve/inspect` to return the full pipeline trace (BM25 results, Dense results, RRF scores, Reranker scores, and latencies).
6. **Configuration**: Extract `bm25_top_k`, `dense_top_k`, `fusion_top_k`, `final_top_k`, and `rrf_k` into a centralized `config.py` or dict.

## Interfaces to be Extended
- `RetrievedChunk` will be extended (if not already present) to explicitly support `rrf_score`, `reranker_score`, and `final_rank`.
- `endpoints.py` will gain the `/retrieve/hybrid` and `/retrieve/inspect` endpoints.

## Potential Compatibility Issues
- The `cross-encoder` model might consume too much VRAM alongside the dense embedding model. I will ensure they are cleanly loaded and explicitly batched. If CUDA OOM occurs, they must gracefully fallback to CPU.
- We must ensure we don't accidentally mutate the provenance metadata when combining or mutating chunk objects during the fusion stage.

## Test Strategy
- **RRF**: Unit tests for rank inversion, score collision, empty lists, and disjoint sets.
- **Reranker**: Unit tests mocking the model to verify score mapping and candidate slicing.
- **Hybrid Service**: Integration tests proving parallel retrieval execution and correct candidate flow.
- **Existing Tests**: Run all Phase 2 tests (Chunking, Embeddings, BM25, Dense) to guarantee zero regression.
