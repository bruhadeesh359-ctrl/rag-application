from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List, Any, Dict

T = TypeVar('T')

class APIError(BaseModel):
    code: str = Field(..., description="Application-specific error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional context or validation errors")
    request_id: Optional[str] = Field(None, description="The correlated request ID")
    trace_id: Optional[str] = Field(None, description="The correlated observability trace ID")

class APIResponse(BaseModel, Generic[T]):
    request_id: Optional[str] = Field(None, description="The correlated request ID")
    data: Optional[T] = Field(None, description="The primary response payload")
    meta: Optional[Dict[str, Any]] = Field(None, description="Pagination or other metadata")

class PaginatedMeta(BaseModel):
    page: int
    page_size: int
    total: Optional[int] = None

class PaginatedResponse(BaseModel, Generic[T]):
    request_id: Optional[str] = None
    data: List[T]
    meta: PaginatedMeta
