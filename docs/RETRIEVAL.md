# Retrieval Architecture & Methodology

The Retrieval subsystem of the RAG Observability Lab leverages a hybrid search methodology combined with cross-encoder reranking. This design guarantees high recall through parallel semantic and keyword search, while maximizing precision via neural reranking.

## 1. Sparse Retrieval (BM25)
**Purpose:** Ensure exact keyword matches (e.g., proper nouns, specific UUIDs, error codes) are not lost.
**Implementation:** We use `Rank_BM25` (specifically `BM25Okapi`).
**Why it exists:** Dense models often struggle with out-of-vocabulary terms or highly specific identifiers.

## 2. Dense Retrieval (ChromaDB)
**Purpose:** Retrieve documents based on semantic similarity rather than exact lexical overlap.
**Implementation:** `sentence-transformers/all-MiniLM-L6-v2` generating 384-dimensional embeddings, stored and queried via ChromaDB using Approximate Nearest Neighbors (ANN).
**Why it exists:** Keyword search fails when users use synonyms or conceptually similar phrasing.

## 3. Hybrid Fusion: Reciprocal Rank Fusion (RRF)
**Purpose:** Combine the results of Sparse and Dense retrieval into a single ranked list without requiring calibrated confidence scores from both systems.
**Formula:**
`RRF_Score(d) = Σ (1 / (k + rank_i(d)))`
Where `k` is a smoothing constant (typically 60), and `rank_i(d)` is the rank of document `d` in the `i`-th retrieval list.
**Implementation:** `app.services.fusion.RRFFusion`

## 4. Cross-Encoder Reranking
**Purpose:** The RRF list provides high recall but mediocre precision. A cross-encoder evaluates the `(query, document)` pair simultaneously to provide a highly accurate relevance score.
**Implementation:** `cross-encoder/ms-marco-MiniLM-L-6-v2` inside `CrossEncoderReranker`.
**Why rerank?** Bi-encoders (used for dense retrieval) compute embeddings independently, losing contextual nuance. Cross-encoders attend to the query and document together, massively improving the final top-K precision before feeding chunks to the LLM.

## 5. Provenance
Every chunk returned by this pipeline carries a strict `Provenance` object containing the `document_id`, original `filename`, and `chunk_index`. This metadata is never lost and is ultimately used to validate citations in the LLM's final response.
