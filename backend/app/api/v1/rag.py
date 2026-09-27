from fastapi import APIRouter, Depends, HTTPException

from app.schemas.api import APIResponse
from app.schemas.rag_api import RAGQueryRequest, RAGQueryResponseData, RAGInspectResponseData, RetrievedContextResponse
from app.api.dependencies import get_rag_service, get_hybrid_retriever
from app.core.middleware import request_id_ctx_var

router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/query", response_model=APIResponse[RAGQueryResponseData])
async def rag_query(
    request: RAGQueryRequest,
    rag_service = Depends(get_rag_service)
):
    try:
        # Pass experiment_id downstream if we want to trace it
        response_dict = await rag_service.query(request.query)
        
        data = RAGQueryResponseData(
            answer=response_dict["answer"],
            status=response_dict["status"],
            abstained=response_dict.get("abstained", False),
            fallback_reason=response_dict.get("fallback_reason"),
            citations=response_dict.get("citations", []),
            groundedness=response_dict.get("groundedness")
        )
        
        meta = {}
        if request.include_debug:
            meta["debug_info"] = "Enabled trace debugging."
            
        # The trace_id should ideally be extracted from the trace manager if returned
        return APIResponse(
            request_id=request_id_ctx_var.get(),
            data=data,
            meta=meta
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/inspect", response_model=APIResponse[RAGInspectResponseData])
async def rag_inspect(
    request: RAGQueryRequest,
    hybrid_retriever = Depends(get_hybrid_retriever)
):
    try:
        inspection = await hybrid_retriever.retrieve_with_inspector(request.query)
        
        contexts = [
            RetrievedContextResponse(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                text=c.text,
                score=c.score,
                rank=c.rank,
                retrieval_method=c.retrieval_method,
                provenance=c.provenance.model_dump() if c.provenance else None
            )
            for c in inspection.get("reranked_results", [])
        ]
        
        data = RAGInspectResponseData(
            query=inspection["query"],
            status="inspected",
            contexts=contexts
        )
        
        meta = {
            "timing_ms": inspection.get("timing_ms", {})
        }
        
        return APIResponse(
            request_id=request_id_ctx_var.get(),
            data=data,
            meta=meta
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
