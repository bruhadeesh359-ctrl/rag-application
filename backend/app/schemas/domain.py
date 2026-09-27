from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class DocumentMetadata(BaseModel):
    filename: str
    file_type: str
    file_size_bytes: int
    created_at: str
    additional_info: Dict[str, Any] = Field(default_factory=dict)

class DocumentCreate(BaseModel):
    document_id: str
    metadata: DocumentMetadata
    raw_content: str

class Provenance(BaseModel):
    document_id: str
    filename: str
    page: Optional[int] = None
    section: Optional[str] = None
    chunk_index: int
    source_location: Optional[str] = None

class ChunkCreate(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    provenance: Provenance

class Chunk(ChunkCreate):
    pass

class RetrievedChunk(Chunk):
    score: float
    rank: int
    retrieval_method: str # e.g. "bm25", "dense", "rrf", "cross-encoder"
    
    # Phase 3 Fields (Optional per-stage scores)
    original_rank: Optional[int] = None
    rrf_score: Optional[float] = None
    reranker_score: Optional[float] = None
    final_rank: Optional[int] = None

class QueryContext(BaseModel):
    query_id: str
    question: str
    retrieved_chunks: List[RetrievedChunk]

class ExtractedClaim(BaseModel):
    claim_id: str
    text: str
    source_chunk_ids: List[str]

class GroundednessResult(BaseModel):
    supported_claims: int
    total_claims: int
    claims: List[Dict[str, Any]] # e.g., {"claim_id": "...", "status": "supported/unsupported", "reason": "..."}

class GenerationResult(BaseModel):
    answer: str
    claims: List[ExtractedClaim]
    groundedness: GroundednessResult
    fallback_triggered: bool = False
