from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any

from app.core.database import get_db
from app.models.sql_models import SQLTrace, SQLSpan, SQLErrorEvent
from app.schemas.api import APIResponse, PaginatedResponse, PaginatedMeta

router = APIRouter(prefix="/observability", tags=["observability"])

@router.get("/traces", response_model=PaginatedResponse[Dict[str, Any]])
async def get_traces(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * page_size
    stmt = select(SQLTrace).order_by(SQLTrace.start_time.desc()).offset(offset).limit(page_size)
    result = await session.execute(stmt)
    traces = result.scalars().all()
    
    data = [
        {
            "trace_id": t.trace_id,
            "request_id": t.request_id,
            "experiment_id": t.experiment_id,
            "start_time": t.start_time.isoformat() if t.start_time else None,
            "end_time": t.end_time.isoformat() if t.end_time else None,
            "duration_ms": t.duration_ms,
            "status": t.status,
            "total_tokens": t.total_tokens
        }
        for t in traces
    ]
    
    return PaginatedResponse(
        data=data,
        meta=PaginatedMeta(page=page, page_size=page_size)
    )

@router.get("/traces/{trace_id}", response_model=APIResponse[Dict[str, Any]])
async def get_trace(
    trace_id: str,
    session: AsyncSession = Depends(get_db)
):
    stmt = select(SQLTrace).options(
        selectinload(SQLTrace.spans),
        selectinload(SQLTrace.errors)
    ).filter(SQLTrace.trace_id == trace_id)
    
    result = await session.execute(stmt)
    trace = result.scalars().first()
    
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
        
    data = {
        "trace_id": trace.trace_id,
        "request_id": trace.request_id,
        "experiment_id": trace.experiment_id,
        "start_time": trace.start_time.isoformat() if trace.start_time else None,
        "end_time": trace.end_time.isoformat() if trace.end_time else None,
        "duration_ms": trace.duration_ms,
        "status": trace.status,
        "token_usage": {
            "input_tokens": trace.input_tokens,
            "output_tokens": trace.output_tokens,
            "total_tokens": trace.total_tokens,
            "token_source": trace.token_source
        } if trace.total_tokens is not None else None,
        "spans": [
            {
                "span_id": s.span_id,
                "parent_span_id": s.parent_span_id,
                "stage": s.stage,
                "duration_ms": s.duration_ms,
                "status": s.status,
            }
            for s in trace.spans
        ],
        "errors": [
            {
                "error_id": e.error_id,
                "span_id": e.span_id,
                "category": e.category,
                "message": e.message
            }
            for e in trace.errors
        ]
    }
    
    return APIResponse(data=data)

@router.get("/summary", response_model=APIResponse[Dict[str, Any]])
async def get_summary(
    session: AsyncSession = Depends(get_db)
):
    # This remains simple for demonstration. In prod, use SQL aggregation.
    result = await session.execute(select(SQLTrace))
    traces = result.scalars().all()
    
    total = len(traces)
    if total == 0:
        return APIResponse(data={"status": "NOT_YET_MEASURED", "total_requests": 0})
        
    successful = sum(1 for t in traces if t.status == "success")
    abstained = sum(1 for t in traces if t.status == "abstained")
    failed = sum(1 for t in traces if t.status == "error")
    
    durations = sorted([t.duration_ms for t in traces if t.duration_ms is not None])
    p50 = durations[int(len(durations)*0.50)] if durations else 0
    p95 = durations[int(len(durations)*0.95)] if durations else 0
    
    data = {
        "total_requests": total,
        "successful_requests": successful,
        "abstained_requests": abstained,
        "failed_requests": failed,
        "average_latency_ms": sum(durations)/len(durations) if durations else 0,
        "p50_latency_ms": p50,
        "p95_latency_ms": p95
    }
    
    return APIResponse(data=data)
