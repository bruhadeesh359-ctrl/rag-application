from functools import lru_cache
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.core.database import get_db
from app.services.sqlite_storage import SQLiteStorage
from app.services.vector_store import ChromaVectorStorage
from app.services.sparse_index import BM25SparseIndex
from app.services.embeddings import EmbeddingService
from app.services.retrievers import DenseRetriever, SparseRetriever
from app.services.hybrid_retriever import HybridRetriever
from app.services.fusion import RRFFusion
from app.services.reranker import CrossEncoderReranker
from app.services.rag_service import RAGService

# Lazy load expensive services using lru_cache
# This prevents model loading during startup / import time

@lru_cache()
def get_relational_storage() -> SQLiteStorage:
    return SQLiteStorage()

@lru_cache()
def get_vector_storage() -> ChromaVectorStorage:
    return ChromaVectorStorage()

@lru_cache()
def get_sparse_index() -> BM25SparseIndex:
    return BM25SparseIndex()

@lru_cache()
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()

@lru_cache()
def get_dense_retriever() -> DenseRetriever:
    return DenseRetriever(
        vector_storage=get_vector_storage(),
        embedding_service=get_embedding_service(),
        relational_storage=get_relational_storage()
    )

@lru_cache()
def get_sparse_retriever() -> SparseRetriever:
    return SparseRetriever(
        sparse_index=get_sparse_index(),
        relational_storage=get_relational_storage()
    )

@lru_cache()
def get_fusion_service() -> RRFFusion:
    return RRFFusion()

@lru_cache()
def get_reranker_service() -> CrossEncoderReranker:
    return CrossEncoderReranker()

@lru_cache()
def get_hybrid_retriever() -> HybridRetriever:
    return HybridRetriever(
        sparse_retriever=get_sparse_retriever(),
        dense_retriever=get_dense_retriever(),
        fusion_service=get_fusion_service(),
        reranker_service=get_reranker_service()
    )

@lru_cache()
def get_rag_service() -> RAGService:
    return RAGService(hybrid_retriever=get_hybrid_retriever())

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session
