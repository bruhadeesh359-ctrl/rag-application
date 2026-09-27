import json
import time
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from evaluation.schemas import (
    EvaluationQuery, 
    ExperimentConfig, 
    ExperimentResult, 
    RetrievalMetrics, 
    GenerationMetrics, 
    LatencyMetrics
)
from evaluation.metrics.retrieval import recall_at_k, mrr, ndcg_at_k
from evaluation.metrics.generation import compute_generation_metrics

class Evaluator:
    def __init__(self, retriever=None, rag_service=None):
        self.retriever = retriever
        self.rag_service = rag_service

    async def run_retrieval_evaluation(
        self, 
        dataset_path: str, 
        config: ExperimentConfig
    ) -> ExperimentResult:
        if not self.retriever:
            raise ValueError("Retriever must be provided for retrieval evaluation.")

        queries = self._load_dataset(dataset_path)
        
        r1, r3, r5, r10 = [], [], [], []
        mrrs = []
        ndcg5, ndcg10 = [], []
        latencies = []
        errors = []

        for q in queries:
            start_time = time.time()
            try:
                # We fetch deep because we want to measure NDCG@10
                chunks = await self.retriever.retrieve(q.query, top_k=10)
                latency_ms = (time.time() - start_time) * 1000
                latencies.append(latency_ms)

                retrieved_ids = [c.chunk_id for c in chunks]
                rel_ids = q.relevant_chunk_ids

                r1.append(recall_at_k(retrieved_ids, rel_ids, 1))
                r3.append(recall_at_k(retrieved_ids, rel_ids, 3))
                r5.append(recall_at_k(retrieved_ids, rel_ids, 5))
                r10.append(recall_at_k(retrieved_ids, rel_ids, 10))
                
                mrrs.append(mrr(retrieved_ids, rel_ids))
                ndcg5.append(ndcg_at_k(retrieved_ids, rel_ids, 5))
                ndcg10.append(ndcg_at_k(retrieved_ids, rel_ids, 10))
                
            except Exception as e:
                errors.append({
                    "query_id": q.query_id,
                    "error": str(e),
                    "category": "RETRIEVAL_MISS"
                })

        retrieval_metrics = RetrievalMetrics(
            recall_at_1=np.mean(r1) if r1 else 0.0,
            recall_at_3=np.mean(r3) if r3 else 0.0,
            recall_at_5=np.mean(r5) if r5 else 0.0,
            recall_at_10=np.mean(r10) if r10 else 0.0,
            mrr=np.mean(mrrs) if mrrs else 0.0,
            ndcg_at_5=np.mean(ndcg5) if ndcg5 else 0.0,
            ndcg_at_10=np.mean(ndcg10) if ndcg10 else 0.0
        )
        
        latency_metrics = LatencyMetrics(
            retrieval_ms_p50=np.percentile(latencies, 50) if latencies else 0.0,
            retrieval_ms_p95=np.percentile(latencies, 95) if latencies else 0.0,
            total_ms_p50=np.percentile(latencies, 50) if latencies else 0.0
        )

        return ExperimentResult(
            config=config,
            retrieval_metrics=retrieval_metrics,
            latency_metrics=latency_metrics,
            errors=errors,
            timestamp=datetime.now().isoformat()
        )

    def _load_dataset(self, path: str) -> List[EvaluationQuery]:
        queries = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    queries.append(EvaluationQuery.model_validate_json(line))
        return queries
