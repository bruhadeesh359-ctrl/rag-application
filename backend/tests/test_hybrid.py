import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.services.hybrid_retriever import HybridRetriever
from app.schemas.domain import RetrievedChunk, Provenance
from app.core.config import settings

def create_mock_chunk(chunk_id: str, rank: int, score: float, method: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_1",
        text=f"Content {chunk_id}",
        provenance=Provenance(document_id="doc_1", filename="f.pdf", chunk_index=0),
        score=score,
        rank=rank,
        retrieval_method=method
    )

@pytest.mark.asyncio
async def test_hybrid_retriever_basic():
    # Mock Retrievers
    mock_sparse = AsyncMock()
    mock_sparse.retrieve.return_value = [
        create_mock_chunk("chunk_A", 1, 0.9, "bm25"),
        create_mock_chunk("chunk_B", 2, 0.8, "bm25")
    ]
    
    mock_dense = AsyncMock()
    mock_dense.retrieve.return_value = [
        create_mock_chunk("chunk_B", 1, 0.85, "dense"),
        create_mock_chunk("chunk_C", 2, 0.7, "dense")
    ]
    
    # Mock Fusion
    mock_fusion = MagicMock()
    fused_candidates = [
        create_mock_chunk("chunk_B", 1, 0.05, "rrf"),
        create_mock_chunk("chunk_A", 2, 0.04, "rrf"),
        create_mock_chunk("chunk_C", 3, 0.03, "rrf")
    ]
    mock_fusion.fuse.return_value = fused_candidates
    
    # Mock Reranker
    mock_reranker = MagicMock()
    final_candidates = [
        create_mock_chunk("chunk_B", 1, 0.99, "cross-encoder"),
        create_mock_chunk("chunk_C", 2, 0.88, "cross-encoder"),
        create_mock_chunk("chunk_A", 3, 0.11, "cross-encoder")
    ]
    mock_reranker.rerank.return_value = final_candidates
    
    hybrid = HybridRetriever(
        sparse_retriever=mock_sparse,
        dense_retriever=mock_dense,
        fusion_service=mock_fusion,
        reranker_service=mock_reranker
    )
    
    results = await hybrid.retrieve("test query")
    
    assert len(results) == 3
    assert results[0].chunk_id == "chunk_B"
    assert results[0].score == 0.99
    
    # Verify method calls
    mock_sparse.retrieve.assert_awaited_once_with("test query", top_k=settings.retrieval.bm25_top_k)
    mock_dense.retrieve.assert_awaited_once_with("test query", top_k=settings.retrieval.dense_top_k)
    mock_fusion.fuse.assert_called_once()
    mock_reranker.rerank.assert_called_once_with("test query", fused_candidates, top_k=settings.retrieval.final_top_k)

@pytest.mark.asyncio
async def test_hybrid_retriever_inspector():
    # Similar setup to above, but test the retrieve_with_inspector output
    mock_sparse = AsyncMock()
    mock_sparse.retrieve.return_value = []
    
    mock_dense = AsyncMock()
    mock_dense.retrieve.return_value = []
    
    hybrid = HybridRetriever(
        sparse_retriever=mock_sparse,
        dense_retriever=mock_dense
    )
    
    response = await hybrid.retrieve_with_inspector("test query")
    
    assert response["query"] == "test query"
    assert "timings" in response
    assert "total_ms" in response["timings"]
    assert "base_retrieval_ms" in response["timings"]
    assert response["bm25_results"] == []
    assert response["dense_results"] == []
