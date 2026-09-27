from abc import ABC, abstractmethod
from typing import Dict, Any, List

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> Dict[str, Any]:
        """
        Must return a dict containing at least:
        - 'text': the generated text response
        - 'input_tokens': int
        - 'output_tokens': int
        """
        pass

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-3.1-pro"):
        self.api_key = api_key
        self.model_name = model_name
        # In a real implementation, you would use google.generativeai client
        
    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> Dict[str, Any]:
        # Placeholder for actual API call
        # Mocking generation for now to ensure pipeline runs even without API key set.
        
        # Example structure
        # response = await self.client.generate_content(...)
        return {
            "text": "This is a mocked Gemini response based on the provided context.",
            "input_tokens": len(system_prompt.split()) + len(user_prompt.split()),
            "output_tokens": 15
        }
