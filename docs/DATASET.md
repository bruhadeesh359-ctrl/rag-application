# Dataset Documentation

The evaluation datasets used in the RAG Observability Lab are stored locally in JSON format to support the `evaluate_retrieval.py` and `evaluate_rag.py` scripts.

## 1. Corpus Documentation

- **Source:** User-uploaded documents via the `/api/v1/ingestion` endpoints, or pre-seeded offline text corpora.
- **Preprocessing:** Documents are stripped of whitespace artifacts, normalized to standard UTF-8, and tokenized.
- **Chunking Strategy:** 
  - Token-based rolling chunks.
  - Default chunk size: 256 tokens.
  - Overlap: 32 tokens to preserve boundary context.
- **Metadata:** Each chunk retains original document ID, page/section reference (where available), and sequential chunk index.

## 2. Evaluation Datasets

For quantitative evaluations, a JSON dataset (`eval_dataset.json`) is maintained with the following schema:
```json
[
  {
    "query_id": "q1",
    "query": "What is the hybrid retrieval fallback policy?",
    "relevant_document_ids": ["doc_id_123", "doc_id_124"],
    "expected_answer": "The system abstains from generating a response if the top retrieval score falls below the minimum evidence threshold."
  }
]
```

- **Relevance Labeling:** Binary relevance is used for MS MARCO-style evaluation. If a document is in `relevant_document_ids`, it is considered highly relevant.
- **Leakage Prevention:** Great care must be taken to ensure that the evaluation dataset queries are not part of any model training data.
- **Synthetic Data:** *If synthetic query-document pairs are generated for internal testing, they are strictly isolated in `data/synthetic_eval_dataset.json` and are NOT used to report final architecture performance.*

## 3. Limitations
The primary limitation of local evaluation datasets is size. True RAG performance requires evaluation over thousands of diverse queries. Because this is a lab environment, users should import standardized datasets like BEIR or MS MARCO to produce statistically significant results.
