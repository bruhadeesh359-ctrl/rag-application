from fastapi import APIRouter, Depends
import platform
import sys

from app.schemas.api import APIResponse
from app.api.dependencies import get_embedding_service, get_reranker_service

router = APIRouter()

@router.get("/health", response_model=APIResponse[dict])
async def health_check():
    return APIResponse(
        data={
            "status": "ok",
            "service": "rag-platform"
        }
    )

@router.get("/system", response_model=APIResponse[dict])
async def system_info(
    embedding_service = Depends(get_embedding_service),
    reranker_service = Depends(get_reranker_service)
):
    # Only expose safe runtime info
    try:
        import torch
        cuda_available = torch.cuda.is_available()
    except ImportError:
        cuda_available = False
        
    return APIResponse(
        data={
            "status": "READY",
            "service": "rag-platform",
            "runtime": {
                "os": platform.system(),
                "python_version": sys.version.split(" ")[0],
                "cuda_available": cuda_available
            },
            "models": {
                "embedding_model": embedding_service.get_model_name(),
                "reranker_model": reranker_service.model.config.name_or_path if hasattr(reranker_service, 'model') else "cross-encoder/ms-marco-MiniLM-L-6-v2"
            }
        }
    )
