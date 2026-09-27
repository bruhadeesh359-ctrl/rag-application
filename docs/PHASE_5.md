# Phase 5: RAG Evaluation & Benchmarking

## Overview
Phase 5 introduces a robust offline evaluation, benchmarking, and experiment tracking framework. It separates Retrieval evaluation (cost-free, deterministic) from Generation evaluation (LLM-based) and stores rigorous metric outputs for side-by-side ablation comparisons.

## Evaluation Architecture

### Layer 1: Retrieval Evaluation (Deterministic)
Evaluates whether the system can find the right chunks mathematically, bypassing the LLM. 
Metrics implemented:
- **Recall@K (1, 3, 5, 10)**: Did the relevant chunk appear in the top K?
- **MRR (Mean Reciprocal Rank)**: How high was the first relevant chunk ranked?
- **NDCG@K (Normalized Discounted Cumulative Gain)**: Grading the overall ranking quality, heavily penalizing relevant chunks that are buried at the bottom.

### Layer 2: Generation Evaluation (LLM-Assisted)
Evaluates how well the LLM utilized the retrieved context.
Metrics aggregated:
- **Citation Coverage**: `total_valid_citations / total_expected_citations`. Determines if the LLM hallucinated fake `[Sx]` citation IDs.
- **Groundedness**: `supported_claims / total_claims`. Uses the LLM-as-a-judge to detect ungrounded factual hallucination.
- **Abstention Rate**: How often the system intentionally falls back due to low `minimum_evidence_score`.

### Layer 3: End-to-End Evaluation
Tracks operational metrics spanning the complete RAG query lifecycle:
- **Latency (p50, p95)**: Exact millisecond tracking for vector searches vs LLM generation.
- **Error Taxonomy**: Categorized pipeline failures (e.g., `RETRIEVAL_MISS`).

## The CLI Runner
You can run deterministic evaluation offline without consuming Gemini tokens.
```powershell
# Run BM25 Baseline
python -m evaluation.run_eval --dataset evaluation/datasets/starter_dataset.jsonl --experiment bm25_baseline --retriever bm25

# Run Dense Retrieval
python -m evaluation.run_eval --dataset evaluation/datasets/starter_dataset.jsonl --experiment dense_baseline --retriever dense
```

## Results & Tracking
Each experiment is saved into `evaluation/results/<experiment_id>_<timestamp>/`.
- `config.json`: The hyper-parameters.
- `retrieval_metrics.json`: The aggregated Recall, MRR, NDCG.
- `errors.json`: The query-by-query failure logs.

## Rule: No Fake Statistics
If pricing and exact token usage are not exposed by the async Gemini SDK, the metrics correctly output `0.0` or are omitted from the tracker. The evaluation framework refuses to fabricate plausible numbers.
