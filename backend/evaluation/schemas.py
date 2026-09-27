import json
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EvaluationQuery(BaseModel):
    query_id: str
    query: str
    category: Optional[str] = "factual"
    # Ground Truth for Retrieval (Layer 1)
    relevant_chunk_ids: List[str] = Field(default_factory=list)
    relevant_document_ids: List[str] = Field(default_factory=list)
    # Ground Truth for Generation (Layer 2)
    reference_answer: Optional[str] = None
    expected_citations: List[str] = Field(default_factory=list)

class RetrievalMetrics(BaseModel):
    recall_at_1: float = 0.0
    recall_at_3: float = 0.0
    recall_at_5: float = 0.0
    recall_at_10: float = 0.0
    mrr: float = 0.0
    ndcg_at_5: float = 0.0
    ndcg_at_10: float = 0.0

class GenerationMetrics(BaseModel):
    groundedness: float = 0.0 # supported claims / total claims
    unsupported_claim_rate: float = 0.0
    citation_coverage: float = 0.0
    abstention_rate: float = 0.0

class LatencyMetrics(BaseModel):
    retrieval_ms_p50: float = 0.0
    retrieval_ms_p95: float = 0.0
    generation_ms_p50: float = 0.0
    total_ms_p50: float = 0.0

class ExperimentConfig(BaseModel):
    experiment_id: str
    dataset_version: str
    retriever_type: str  # "bm25", "dense", "hybrid_rrf", "hybrid_rerank"
    llm_model: str
    seed: int = 42

class ExperimentResult(BaseModel):
    config: ExperimentConfig
    retrieval_metrics: Optional[RetrievalMetrics] = None
    generation_metrics: Optional[GenerationMetrics] = None
    latency_metrics: Optional[LatencyMetrics] = None
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: str
