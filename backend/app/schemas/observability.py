from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ErrorCategory:
    INGESTION_ERROR = "INGESTION_ERROR"
    PARSING_ERROR = "PARSING_ERROR"
    CHUNKING_ERROR = "CHUNKING_ERROR"
    STORAGE_ERROR = "STORAGE_ERROR"
    EMBEDDING_ERROR = "EMBEDDING_ERROR"
    BM25_ERROR = "BM25_ERROR"
    VECTOR_STORE_ERROR = "VECTOR_STORE_ERROR"
    RRF_ERROR = "RRF_ERROR"
    RERANKER_ERROR = "RERANKER_ERROR"
    CONTEXT_ERROR = "CONTEXT_ERROR"
    EVIDENCE_ERROR = "EVIDENCE_ERROR"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_AUTH_ERROR = "LLM_AUTH_ERROR"
    LLM_RATE_LIMIT = "LLM_RATE_LIMIT"
    LLM_PROVIDER_ERROR = "LLM_PROVIDER_ERROR"
    LLM_INVALID_OUTPUT = "LLM_INVALID_OUTPUT"
    CITATION_ERROR = "CITATION_ERROR"
    GROUNDEDNESS_ERROR = "GROUNDEDNESS_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    SECURITY_ERROR = "SECURITY_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

class SeverityLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class TokenUsage(BaseModel):
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    token_source: str = "actual" # or "estimated"

class CostEstimate(BaseModel):
    input_cost: Optional[float] = None
    output_cost: Optional[float] = None
    total_cost: Optional[float] = None
    currency: str = "USD"
    pricing_version: Optional[str] = None
    cost_status: str = "unavailable"

class ErrorEvent(BaseModel):
    error_id: str
    trace_id: str
    span_id: Optional[str] = None
    category: str
    severity: str
    message: str
    timestamp: datetime
    retryable: bool = False
    component: str

class Span(BaseModel):
    span_id: str
    trace_id: str
    parent_span_id: Optional[str] = None
    stage: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str = "running"
    attributes: Dict[str, Any] = Field(default_factory=dict)
    errors: List[ErrorEvent] = Field(default_factory=list) # Track inline errors if needed

class Trace(BaseModel):
    trace_id: str
    request_id: Optional[str] = None
    experiment_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    status: str = "running"
    token_usage: Optional[TokenUsage] = None
    cost: Optional[CostEstimate] = None
    spans: List[Span] = Field(default_factory=list)
    errors: List[ErrorEvent] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)

class ObservabilitySummary(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    abstentions: int
    average_latency_ms: float
    p50_latency_ms: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    p99_latency_ms: Optional[float] = None
    llm_failures: int
    retrieval_failures: int
    prompt_injection_events: int
