import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.services.groundedness import GroundednessAnalyzer
from app.schemas.domain import GroundednessResult

@pytest.mark.asyncio
async def test_groundedness_analyzer_success():
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = """
    {
        "claims": [
            {
                "claim_id": "C1",
                "text": "The refund period is 30 days.",
                "status": "supported",
                "reason": "Explicitly stated",
                "source_chunk_ids": ["S1"]
            },
            {
                "claim_id": "C2",
                "text": "The company was founded in 1990.",
                "status": "unsupported",
                "reason": "Not mentioned in context",
                "source_chunk_ids": []
            }
        ]
    }
    """
    
    analyzer = GroundednessAnalyzer(mock_llm)
    
    result = await analyzer.analyze("Answer", "Context", {"S1": MagicMock()})
    
    assert result.total_claims == 2
    assert result.supported_claims == 1
    assert result.claims[0]["status"] == "supported"
    assert result.claims[1]["status"] == "unsupported"

@pytest.mark.asyncio
async def test_groundedness_analyzer_json_failure():
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "This is not JSON at all."
    
    analyzer = GroundednessAnalyzer(mock_llm)
    
    result = await analyzer.analyze("Answer", "Context", {})
    
    assert result.total_claims == 0
    assert result.supported_claims == 0
    assert "error" in result.claims[0]
