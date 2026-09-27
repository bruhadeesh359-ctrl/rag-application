from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import time
import uuid
from datetime import datetime, timezone
import contextvars

from app.schemas.observability import Trace, Span, ErrorEvent, TokenUsage, CostEstimate, ErrorCategory, SeverityLevel

# Context variables for distributed-style tracking within a single async request
current_trace: contextvars.ContextVar[Optional[Trace]] = contextvars.ContextVar("current_trace", default=None)
current_span_stack: contextvars.ContextVar[List[Span]] = contextvars.ContextVar("current_span_stack", default=[])

class TraceManager:
    def __init__(self, storage=None):
        self.storage = storage

    def start_trace(self, request_id: str = None, experiment_id: str = None) -> Trace:
        trace_id = f"trace_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        trace = Trace(
            trace_id=trace_id,
            request_id=request_id,
            experiment_id=experiment_id,
            start_time=datetime.utcnow(),
            status="running"
        )
        current_trace.set(trace)
        current_span_stack.set([])
        return trace

    def get_current_trace(self) -> Optional[Trace]:
        return current_trace.get()

    def start_span(self, stage: str, attributes: Dict[str, Any] = None) -> Span:
        trace = current_trace.get()
        if not trace:
            # If no trace is active, create a dummy trace to avoid crashing (fallback)
            trace = self.start_trace()

        stack = current_span_stack.get()
        parent_span_id = stack[-1].span_id if stack else None
        
        span = Span(
            span_id=f"span_{uuid.uuid4().hex[:8]}",
            trace_id=trace.trace_id,
            parent_span_id=parent_span_id,
            stage=stage,
            start_time=datetime.utcnow(),
            attributes=attributes or {}
        )
        
        trace.spans.append(span)
        new_stack = stack.copy()
        new_stack.append(span)
        current_span_stack.set(new_stack)
        return span

    def end_span(self, span: Span, status: str = "success", attributes: Dict[str, Any] = None):
        span.end_time = datetime.utcnow()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000.0
        span.status = status
        if attributes:
            span.attributes.update(attributes)
            
        stack = current_span_stack.get()
        if stack and stack[-1].span_id == span.span_id:
            new_stack = stack[:-1]
            current_span_stack.set(new_stack)

    def record_error(self, category: str, message: str, severity: str = SeverityLevel.ERROR, retryable: bool = False, component: str = "unknown"):
        trace = current_trace.get()
        if not trace:
            return

        stack = current_span_stack.get()
        span_id = stack[-1].span_id if stack else None
        
        error = ErrorEvent(
            error_id=f"err_{uuid.uuid4().hex[:8]}",
            trace_id=trace.trace_id,
            span_id=span_id,
            category=category,
            severity=severity,
            message=message, # Assuming secrets are scrubbed before this call
            timestamp=datetime.utcnow(),
            retryable=retryable,
            component=component
        )
        
        trace.errors.append(error)
        trace.status = "error"
        if stack:
            stack[-1].status = "error"
            stack[-1].errors.append(error)

    async def end_trace(self) -> Optional[Trace]:
        trace = current_trace.get()
        if not trace:
            return None
            
        trace.end_time = datetime.utcnow()
        trace.duration_ms = (trace.end_time - trace.start_time).total_seconds() * 1000.0
        if trace.status == "running":
            trace.status = "success"
            
        # Clean up context
        current_trace.set(None)
        current_span_stack.set([])
        
        if self.storage:
            await self.storage.save_trace(trace)
            
        return trace

tracer = TraceManager()

