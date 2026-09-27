from pydantic import BaseModel
from typing import Optional

class RRFCfg(BaseModel):
    enabled: bool = True
    k: int = 60
    bm25_weight: float = 1.0
    dense_weight: float = 1.0

class RerankerCfg(BaseModel):
    enabled: bool = True
    model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    batch_size: int = 8
    device: str = "auto"

class RetrievalCfg(BaseModel):
    bm25_top_k: int = 20
    dense_top_k: int = 20
    fusion_top_k: int = 20
    final_top_k: int = 5
    
    rrf: RRFCfg = RRFCfg()
    reranker: RerankerCfg = RerankerCfg()

class GenerationCfg(BaseModel):
    provider: str = "gemini"
    model: str = "gemini-flash-latest"
    temperature: float = 0.0
    max_output_tokens: int = 1024
    timeout_seconds: int = 30
    max_retries: int = 2

class EvidenceCfg(BaseModel):
    minimum_evidence_score: float = -10.0  # Tuned for CrossEncoder raw logits
    minimum_context_chunks: int = 1

class Settings(BaseModel):
    retrieval: RetrievalCfg = RetrievalCfg()
    generation: GenerationCfg = GenerationCfg()
    evidence: EvidenceCfg = EvidenceCfg()

settings = Settings()
