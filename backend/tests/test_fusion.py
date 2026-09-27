import pytest
from app.services.fusion import RRFFusion
from app.schemas.domain import RetrievedChunk, Provenance
from app.core.config import settings

def create_mock_chunk(chunk_id: str, rank: int, method: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_1",
        text=f"Content of {chunk_id}",
        provenance=Provenance(document_id="doc_1", filename="test.pdf", chunk_index=0),
        score=0.9,
        rank=rank,
        retrieval_method=method
    )

def test_rrf_fusion_basic():
    # Setup
    fusion = RRFFusion()
    
    # Sparse puts chunk_1 at rank 1, chunk_2 at rank 2
    sparse = [
        create_mock_chunk("chunk_1", 1, "bm25"),
        create_mock_chunk("chunk_2", 2, "bm25"),
    ]
    
    # Dense puts chunk_2 at rank 1, chunk_1 at rank 2
    dense = [
        create_mock_chunk("chunk_2", 1, "dense"),
        create_mock_chunk("chunk_1", 2, "dense"),
    ]
    
    fused = fusion.fuse(sparse, dense)
    
    assert len(fused) == 2
    
    # chunk_1 score: 1/(60+1) + 1/(60+2) = 1/61 + 1/62 = 0.01639 + 0.01612 = 0.03251
    # chunk_2 score: 1/(60+2) + 1/(60+1) = 0.03251
    # They should have the same RRF score. Let's just verify they are the top 2.
    assert fused[0].chunk_id in ["chunk_1", "chunk_2"]
    assert fused[1].chunk_id in ["chunk_1", "chunk_2"]
    
    # Verify provenance preserved
    assert fused[0].provenance.document_id == "doc_1"
    assert fused[0].retrieval_method == "rrf"
    assert fused[0].rrf_score > 0

def test_rrf_fusion_disjoint():
    fusion = RRFFusion()
    
    sparse = [create_mock_chunk("chunk_1", 1, "bm25")]
    dense = [create_mock_chunk("chunk_2", 1, "dense")]
    
    fused = fusion.fuse(sparse, dense)
    
    assert len(fused) == 2
    # Since both are rank 1 in their respective lists, their scores will be 1/61
    assert abs(fused[0].rrf_score - 1/61) < 1e-5
    assert abs(fused[1].rrf_score - 1/61) < 1e-5

def test_rrf_fusion_limit():
    fusion = RRFFusion()
    
    sparse = [
        create_mock_chunk("chunk_1", 1, "bm25"),
        create_mock_chunk("chunk_2", 2, "bm25"),
        create_mock_chunk("chunk_3", 3, "bm25"),
    ]
    dense = []
    
    # Ask for top 2
    fused = fusion.fuse(sparse, dense, top_k=2)
    assert len(fused) == 2
    assert fused[0].chunk_id == "chunk_1"
    assert fused[1].chunk_id == "chunk_2"
    
def test_rrf_disabled():
    # temporarily disable
    original = settings.retrieval.rrf.enabled
    settings.retrieval.rrf.enabled = False
    
    try:
        fusion = RRFFusion()
        sparse = [create_mock_chunk("chunk_1", 1, "bm25")]
        dense = [create_mock_chunk("chunk_2", 1, "dense")]
        
        fused = fusion.fuse(sparse, dense)
        
        # When disabled, it should return dense results directly
        assert len(fused) == 1
        assert fused[0].chunk_id == "chunk_2"
    finally:
        settings.retrieval.rrf.enabled = original
