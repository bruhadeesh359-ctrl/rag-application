import pytest
from unittest.mock import MagicMock, patch
from app.services.reranker import CrossEncoderReranker
from app.schemas.domain import RetrievedChunk, Provenance
from app.core.config import settings

def create_mock_chunk(chunk_id: str, text: str, rank: int, method: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_1",
        text=text,
        provenance=Provenance(document_id="doc_1", filename="test.pdf", chunk_index=0),
        score=0.5,
        rank=rank,
        retrieval_method=method,
        original_rank=rank,
        rrf_score=0.1
    )

def test_reranker_basic():
    reranker = CrossEncoderReranker()
    
    # Mock the cross encoder model
    mock_model = MagicMock()
    # Let's say chunk_2 is best (0.9), chunk_1 is worst (0.1), chunk_3 is middle (0.5)
    mock_model.predict.return_value = [0.1, 0.9, 0.5]
    reranker.model = mock_model
    
    candidates = [
        create_mock_chunk("chunk_1", "bad content", 1, "rrf"),
        create_mock_chunk("chunk_2", "excellent content", 2, "rrf"),
        create_mock_chunk("chunk_3", "okay content", 3, "rrf"),
    ]
    
    # Run reranking
    reranked = reranker.rerank("good content", candidates, top_k=2)
    
    assert len(reranked) == 2
    
    # Highest score first
    assert reranked[0].chunk_id == "chunk_2"
    assert reranked[0].score == 0.9
    assert reranked[0].reranker_score == 0.9
    assert reranked[0].final_rank == 1
    assert reranked[0].retrieval_method == "cross-encoder"
    assert reranked[0].rrf_score == 0.1
    
    # Second highest
    assert reranked[1].chunk_id == "chunk_3"
    assert reranked[1].score == 0.5
    assert reranked[1].final_rank == 2

def test_reranker_disabled():
    original = settings.retrieval.reranker.enabled
    settings.retrieval.reranker.enabled = False
    
    try:
        reranker = CrossEncoderReranker()
        
        candidates = [
            create_mock_chunk("chunk_1", "content 1", 1, "rrf"),
            create_mock_chunk("chunk_2", "content 2", 2, "rrf"),
        ]
        
        # When disabled, should just return candidates sliced
        reranked = reranker.rerank("query", candidates, top_k=1)
        
        assert len(reranked) == 1
        assert reranked[0].chunk_id == "chunk_1"
        assert reranked[0].retrieval_method == "rrf" # Not modified
    finally:
        settings.retrieval.reranker.enabled = original
