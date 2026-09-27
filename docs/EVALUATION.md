# Evaluation Framework

The RAG Observability Lab implements a comprehensive offline evaluation framework (Phase 5) to objectively measure the performance of both the Retrieval and Generation components.

## 1. Retrieval Metrics

Retrieval is measured against labeled `(query, relevant_document_ids)` datasets using standard Information Retrieval metrics.

- **Recall@K (Recall@1, Recall@3, Recall@5, Recall@10):** The proportion of relevant documents that appear within the top K results. A Recall@5 of 0.8 means 80% of the relevant documents for a given query were successfully retrieved in the top 5 slots.
- **MRR (Mean Reciprocal Rank):** Measures how high the first relevant document appears in the ranked list. An MRR of 1.0 means the relevant document was perfectly ranked at position 1. An MRR of 0.5 means it was at position 2.
- **NDCG@K (Normalized Discounted Cumulative Gain):** Measures ranking quality, giving higher scores when highly relevant documents appear at the very top of the list.

## 2. Generation Metrics

Generation is evaluated on the final LLM output to ensure factual accuracy and system reliability.

- **Citation Correctness:** Does the output contain syntactically valid citations that map back to the retrieved context?
- **Citation Coverage:** What percentage of the generated sentences contain at least one citation?
- **Groundedness:** Measured via LLM-assisted evaluation (using an LLM judge) or deterministic claim verification. Groundedness = `supported_claims / total_evaluable_claims`.
- **Unsupported Claim Rate:** The inverse of groundedness, highlighting hallucination risks.
- **Abstention Rate / Appropriate Abstention:** The rate at which the system successfully triggers a fallback when provided with queries that have no valid context.

## 3. End-to-End Metrics

- **Latency:** Time-to-first-byte and total request time for the entire pipeline, broken down by retrieval vs. generation phases.
- **Token Usage / Cost:** Number of input and output tokens consumed per request.

## 4. Evaluation Results

*Note: As this is a framework sandbox, large-scale benchmarks over standard datasets (e.g., MS MARCO, FiQA) have **NOT YET BEEN MEASURED** on this hardware.*

**If results do NOT exist, we do NOT fabricate them.**

The offline evaluation scripts (`evaluate_retrieval.py` and `evaluate_rag.py`) can be run locally using custom `evaluation_dataset.json` files to generate these metrics deterministically.
