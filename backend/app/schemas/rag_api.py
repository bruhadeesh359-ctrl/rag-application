from pydantic import BaseModel, Field, conint
from typing import List, Optional, Dict, Any

class RetrievalRequest(BaseModel):
    query: str = Field(..., description="The query string to retrieve contexts for.")
    top_k: conint(gt=0, le=100) = Field(10, description="The maximum number of contexts to retrieve.") # type: ignore
    
class RetrievedContextResponse(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    score: float
    rank: int
    retrieval_method: str
    provenance: Optional[Dict[str, Any]] = None

class RAGQueryRequest(BaseModel):
    query: str = Field(..., description="The user's query.")
    top_k: conint(gt=0, le=100) = Field(10, description="Max chunks to retrieve.") # type: ignore
    experiment_id: Optional[str] = Field(None, description="Optional experiment tracking ID.")
    include_debug: bool = Field(False, description="If true, include detailed retrieval metrics in the response metadata.")

class RAGQueryResponseData(BaseModel):
    answer: str
    status: str
    abstained: bool
    fallback_reason: Optional[str] = None
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    groundedness: Optional[Dict[str, Any]] = None

class RAGInspectResponseData(BaseModel):
    query: str
    status: str
    contexts: List[RetrievedContextResponse]
    citation_mapping: Optional[Dict[str, Any]] = None
    validation_results: Optional[Dict[str, Any]] = None
