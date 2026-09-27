from dotenv import load_dotenv
load_dotenv()

from abc import ABC, abstractmethod
import os
import logging
import asyncio
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMError(Exception):
    pass

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_instruction: str, prompt: str) -> str:
        """Generates a text response from the LLM."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verifies the provider is configured correctly."""
        pass

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = settings.generation.model
        self.temperature = settings.generation.temperature
        self.max_output_tokens = settings.generation.max_output_tokens
        self.max_retries = settings.generation.max_retries
        self.timeout = settings.generation.timeout_seconds
        self.last_token_usage = None
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def health_check(self) -> bool:
        return self.api_key is not None and self.client is not None

    async def generate(self, system_instruction: str, prompt: str) -> str:
        if not self.health_check():
            raise LLMError("GEMINI_API_KEY is not set or client failed to initialize.")

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens
        )
        
        for attempt in range(self.max_retries + 1):
            try:
                # We use asyncio.to_thread since the synchronous client blocks
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.models.generate_content,
                        model=self.model,
                        contents=prompt,
                        config=config
                    ),
                    timeout=self.timeout
                )
                
                if response and response.text:
                    if hasattr(response, "usage_metadata") and response.usage_metadata:
                        self.last_token_usage = {
                            "input_tokens": response.usage_metadata.prompt_token_count,
                            "output_tokens": response.usage_metadata.candidates_token_count,
                            "total_tokens": response.usage_metadata.total_token_count
                        }
                    else:
                        self.last_token_usage = None
                    return response.text
                
                raise LLMError("Empty response from Gemini API.")
                
            except asyncio.TimeoutError:
                logger.error(f"Gemini API timeout on attempt {attempt + 1}")
                if attempt == self.max_retries:
                    raise LLMError("LLM_TIMEOUT: Request timed out after all retries.")
            except Exception as e:
                # Catch Rate limit, provider errors, etc.
                err_msg = str(e)
                logger.error(f"Gemini API error: {err_msg}")
                
                # Do not retry on Auth Error or Invalid Request
                if "403" in err_msg or "401" in err_msg or "API_KEY_INVALID" in err_msg:
                    raise LLMError(f"LLM_AUTH_ERROR: {err_msg}")
                    
                if attempt == self.max_retries:
                    raise LLMError(f"LLM_PROVIDER_ERROR: {err_msg}")
                    
                # Exponential backoff for retries
                await asyncio.sleep(2 ** attempt)
                
        raise LLMError("LLM_PROVIDER_ERROR: Failed after all retries.")

def get_llm_provider() -> LLMProvider:
    """Factory to get the configured LLM provider."""
    if settings.generation.provider == "gemini":
        return GeminiProvider()
    raise ValueError(f"Unknown LLM provider: {settings.generation.provider}")
