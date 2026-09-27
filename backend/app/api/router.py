from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.retrieval import router as retrieval_router
from app.api.v1.rag import router as rag_router
from app.api.v1.evaluation import router as evaluation_router
from app.api.v1.observability import router as observability_router
from app.api.v1.experiments import router as experiments_router

router = APIRouter()

router.include_router(health_router)
router.include_router(ingestion_router)
router.include_router(retrieval_router)
router.include_router(rag_router)
router.include_router(evaluation_router)
router.include_router(observability_router)
router.include_router(experiments_router)
