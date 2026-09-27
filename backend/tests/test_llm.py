import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock
from app.core.llm import GeminiProvider, LLMError
from app.core.config import settings

@pytest.fixture
def mock_gemini_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    # speed up retries for tests
    monkeypatch.setattr(settings.generation, "timeout_seconds", 1)
    monkeypatch.setattr(settings.generation, "max_retries", 1)

@pytest.mark.asyncio
async def test_gemini_provider_success(mock_gemini_env):
    provider = GeminiProvider()
    assert provider.health_check() is True

    # Mock the internal client behavior
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is a generated response."
    mock_client.models.generate_content.return_value = mock_response
    provider.client = mock_client

    result = await provider.generate("System instruction", "Prompt text")
    assert result == "This is a generated response."
    mock_client.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_gemini_provider_timeout(mock_gemini_env):
    provider = GeminiProvider()
    
    mock_client = MagicMock()
    
    # Simulate a slow function that exceeds timeout
    def slow_generate(*args, **kwargs):
        import time
        time.sleep(2)
        return MagicMock(text="Too late")
        
    mock_client.models.generate_content.side_effect = slow_generate
    provider.client = mock_client

    with pytest.raises(LLMError) as exc_info:
        await provider.generate("System", "Prompt")
        
    assert "LLM_TIMEOUT" in str(exc_info.value)

@pytest.mark.asyncio
async def test_gemini_provider_auth_error(mock_gemini_env):
    provider = GeminiProvider()
    
    mock_client = MagicMock()
    # Mocking an exception that mimics an auth error
    mock_client.models.generate_content.side_effect = Exception("403 Forbidden: API_KEY_INVALID")
    provider.client = mock_client

    with pytest.raises(LLMError) as exc_info:
        await provider.generate("System", "Prompt")
        
    assert "LLM_AUTH_ERROR" in str(exc_info.value)

@pytest.mark.asyncio
async def test_gemini_provider_missing_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    
    provider = GeminiProvider()
    assert provider.health_check() is False
    
    with pytest.raises(LLMError) as exc_info:
        await provider.generate("System", "Prompt")
        
    assert "GEMINI_API_KEY is not set" in str(exc_info.value)
