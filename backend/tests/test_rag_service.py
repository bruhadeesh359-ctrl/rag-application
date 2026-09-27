import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.rag_service import RAGService
from app.schemas.domain import RetrievedChunk, Provenance
from app.schemas.domain import GroundednessResult

@pytest.fixture
def mock_retriever():
    retriever = AsyncMock()
    retriever.retrieve.return_value = [
        RetrievedChunk(
            chunk_id="c1",
            document_id="d1",
            text="The sky is blue.",
            provenance=Provenance(document_id="d1", filename="f1.pdf", chunk_index=0),
            score=0.9,
            rank=1,
            retrieval_method="rrf"
        )
    ]
    return retriever

@pytest.mark.asyncio
@patch("app.services.rag_service.get_llm_provider")
async def test_rag_service_success(mock_get_llm, mock_retriever):
    mock_llm = AsyncMock()
    del mock_llm.last_token_usage
    
    # We will mock the LLM's generate to just return a string for the main generation,
    # but since groundedness also uses it, we'll patch GroundednessAnalyzer directly for easier testing
    mock_get_llm.return_value = mock_llm
    mock_llm.generate.return_value = "The sky is indeed blue. [S1]"
    
    service = RAGService(mock_retriever)
    
    with patch.object(service.groundedness, 'analyze', new_callable=AsyncMock) as mock_groundedness:
        mock_groundedness.return_value = GroundednessResult(
            supported_claims=1, total_claims=1, claims=[{"status": "supported"}]
        )
        
        result = await service.query("What color is the sky?")
        
        assert result["status"] == "grounded"
        assert result["answer"] == "The sky is indeed blue. [S1]"
        assert result["validation"]["citations_valid"] is True
        assert "S1" in result["citations"]
        
@pytest.mark.asyncio
@patch("app.services.rag_service.get_llm_provider")
async def test_rag_service_fallback_insufficient_evidence(mock_get_llm, mock_retriever):
    # Change retriever to return low score
    mock_retriever.retrieve.return_value = [
        RetrievedChunk(
            chunk_id="c1",
            document_id="d1",
            text="The sky is blue.",
            provenance=Provenance(document_id="d1", filename="f1.pdf", chunk_index=0),
            score=0.001, # Below 0.01 threshold
            rank=1,
            retrieval_method="rrf"
        )
    ]
    
    service = RAGService(mock_retriever)
    result = await service.query("What color is the sky?")
    
    assert result["status"] == "abstained"
    assert "reliably" in result["answer"]
    assert result["reason"] == "Insufficient evidence score."
