# Phase 3: Hybrid Retrieval, RRF Fusion & Cross-Encoder Reranking

## Overview
Phase 3 establishes the hybrid retrieval architecture, fusing the results of dense and sparse (BM25) vector searches and applying a cross-encoder reranker to yield the final context candidates. 

## Hybrid Retrieval Architecture
The system employs parallel retrieval paths which are then synthesized into a single highly-accurate context pool.
1. **BM25 Search (Sparse)**: Retrieves candidates based on exact keyword matching and term frequency. High precision for rare terms.
2. **Dense Search (Embeddings)**: Retrieves candidates using semantic meaning via `sentence-transformers/all-MiniLM-L6-v2`. High recall for conceptually similar phrases.
3. **Reciprocal Rank Fusion (RRF)**: A mathematical algorithm that merges the ranked lists from both retrievers, penalizing low ranks and rewarding documents that appear highly in both lists.
4. **Cross-Encoder Reranker**: The `cross-encoder/ms-marco-MiniLM-L-6-v2` model evaluates the final candidate set by explicitly scoring the relationship between the query and each chunk's text in tandem.

## Why not directly add BM25 and Dense scores?
BM25 scores and Dense Cosine scores exist in completely different scales and distributions. A cosine similarity is bounded `[-1, 1]`, while a BM25 score is an unbounded positive float (e.g. `12.4`, `4.1`). Adding them directly requires complex hyperparameter normalization that is brittle across different domains. RRF avoids this by operating purely on the *rank* (position) of the document, making it statistically robust.

## Configuration
The retrieval parameters are externalized in `app/core/config.py`:
- `bm25_top_k`: Initial depth for sparse retrieval (Default: 20)
- `dense_top_k`: Initial depth for dense retrieval (Default: 20)
- `fusion_top_k`: Number of candidates passed to the reranker (Default: 20)
- `final_top_k`: Final candidates returned to the user (Default: 5)
- `rrf.k`: The constant `k` in the RRF formula (Default: 60)
- `reranker.model`: The cross-encoder model to use.

## Hardware Considerations
The `CrossEncoderReranker` is heavily optimized for constraints like the 6GB RTX 3050.
- Uses `device="auto"`, dynamically binding to CPU or CUDA depending on availability.
- Avoids large monolithic models (uses `MiniLM`).
- Uses batch processing during reranking inference to avoid OOM exceptions.
- CPU fallback allows graceful degradation on unaccelerated hardware.

## API Endpoints
- `POST /api/v1/retrieve/hybrid`: Executes the full Phase 3 pipeline and returns the final `top_k` results.
- `POST /api/v1/retrieve/inspect`: Executes the full pipeline, but returns a detailed JSON object containing the intermediate lists (BM25, Dense, Fused) alongside exact milliseconds taken for each phase. This acts as the core "Observability" debugging hook for retrieval.

## Provenance
Every `RetrievedChunk` carries an embedded `Provenance` model tracing its `document_id`, `filename`, `page`, and `chunk_index`. This provenance model is rigorously passed through `fusion` and `reranking` without mutations.

## Performance Telemetry
The inspector endpoint tracks:
- `base_retrieval_ms`: Parallel BM25 + Dense latency
- `rrf_ms`: Time taken to mathematically fuse the lists
- `reranker_ms`: Time taken for cross-encoder inference
- `total_ms`: End-to-end pipeline latency
