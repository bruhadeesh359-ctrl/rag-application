# Phase 5 Assessment

## Existing Evaluation Capabilities (Phase 1-4)
The current pipeline (Phase 1-4) has robust runtime validation for individual queries. 
- `CitationValidator` checks deterministic citation formatting and exact mapping.
- `GroundednessAnalyzer` checks semantic claim support using an LLM-assisted judge.
- Telemetry captures exact timings per stage.
However, there is **no offline evaluation framework**. We cannot currently benchmark if "BM25 is better than Dense" or "if Cross-Encoder Reranking improves NDCG" because we lack an evaluation dataset, aggregate metric computers (Recall@K, MRR, NDCG), and an experiment runner.

## Missing Evaluation Capabilities
- **Dataset Abstraction**: We need a standard schema for `(query, relevant_chunks, reference_answer, expected_citations)`.
- **Retrieval Metrics**: Recall@K, MRR, NDCG@K.
- **Generation Metrics**: Aggregating the query-level validation into dataset-level averages (Citation Coverage, Groundedness Rate, Unsupported Claim Rate, Abstention Rate).
- **Experiment Tracking**: An engine to record config, metrics, errors, and metadata in `evaluation/results/<experiment_id>/`.
- **Comparison Engine**: A tool to compare experiments side-by-side.
- **CLI & APIs**: For programmatic triggering and automated CI/CD evaluation.

## Dataset Strategy
We will create `evaluation/datasets/evaluation_dataset.schema.json` and a small starter `evaluation_dataset.jsonl`.
The dataset will clearly separate Retrieval Ground Truth (`relevant_chunk_ids`) from Generation Ground Truth (`reference_answer`).

## Experiment Design & Reproducibility
- Experiments will be versioned by `experiment_id` (e.g., `bm25_baseline`, `hybrid_rrf`).
- Random seeds and LLM config will be frozen where possible. 
- Retrieval evaluation will completely bypass the LLM to guarantee deterministic, 0-cost, fast reproduction.

## Implementation Plan
1. **Define Schema**: Create `EvaluationQuery` and `EvaluationResult` schemas.
2. **Implement Metric Calculators**: Create `evaluation/metrics/retrieval.py` for Recall@K, MRR, NDCG.
3. **Implement Evaluator Engine**: Create `evaluation/evaluator.py` that handles routing `(retrieval_only vs end_to_end)` and tracks latency/errors.
4. **Build Experiment Tracker**: Create `evaluation/tracker.py` to persist metadata, config, and metrics to disk in JSON format.
5. **Create CLI**: `backend/evaluation/run_eval.py` using `argparse`.
6. **Expose APIs**: Add `backend/app/api/evaluation.py` and register it with the main FastAPI router.
7. **Write Tests**: Verify math formulas for MRR/NDCG in `tests/test_evaluation.py`.
