from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.schemas.api import APIResponse
from app.schemas.rag_api import RetrievalRequest, RetrievedContextResponse
from app.api.dependencies import get_sparse_retriever, get_dense_retriever, get_hybrid_retriever
from app.core.middleware import request_id_ctx_var

router = APIRouter(prefix="/retrieve", tags=["retrieval"])

def _format_chunks(chunks) -> List[RetrievedContextResponse]:
    return [
        RetrievedContextResponse(
            chunk_id=c.chunk_id,
            document_id=c.document_id,
            text=c.text,
            score=c.score,
            rank=c.rank if hasattr(c, 'rank') else i+1,
            retrieval_method=c.retrieval_method if hasattr(c, 'retrieval_method') else "unknown",
            provenance=c.provenance.dict() if c.provenance else None
        )
        for i, c in enumerate(chunks)
    ]

@router.post("/bm25", response_model=APIResponse[List[RetrievedContextResponse]])
async def retrieve_bm25(
    request: RetrievalRequest,
    retriever = Depends(get_sparse_retriever)
):
    try:
        results = await retriever.retrieve(request.query, request.top_k)
        return APIResponse(
            request_id=request_id_ctx_var.get(),
            data=_format_chunks(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dense", response_model=APIResponse[List[RetrievedContextResponse]])
async def retrieve_dense(
    request: RetrievalRequest,
    retriever = Depends(get_dense_retriever)
):
    try:
        results = await retriever.retrieve(request.query, request.top_k)
        return APIResponse(
            request_id=request_id_ctx_var.get(),
            data=_format_chunks(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hybrid", response_model=APIResponse[List[RetrievedContextResponse]])
async def retrieve_hybrid(
    request: RetrievalRequest,
    retriever = Depends(get_hybrid_retriever)
):
    try:
        results = await retriever.retrieve(request.query)
        # Note: Hybrid limits based on its internal defaults (typically top 5)
        return APIResponse(
            request_id=request_id_ctx_var.get(),
            data=_format_chunks(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
