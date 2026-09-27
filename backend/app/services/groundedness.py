import json
import logging
from typing import Dict, Any, List
from app.core.llm import LLMProvider
from app.schemas.domain import GroundednessResult, ExtractedClaim, RetrievedChunk

logger = logging.getLogger(__name__)

class GroundednessAnalyzer:
    """
    LLM-assisted evaluator that extracts claims from a generated answer
    and verifies if they are strictly entailed by the provided evidence.
    """
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        
    async def analyze(self, answer: str, context_str: str, citation_map: Dict[str, RetrievedChunk]) -> GroundednessResult:
        if not answer.strip() or not context_str.strip():
            return GroundednessResult(supported_claims=0, total_claims=0, claims=[])
            
        system_prompt = """You are a strict groundedness evaluator for a RAG system.
Your job is to:
1. Extract distinct factual claims from the generated answer.
2. Verify if each claim is completely supported by the provided source context.
3. Return the result in STRICT JSON format.

A claim is SUPPORTED only if the context contains explicit evidence for it. If the context is ambiguous, or doesn't mention it, the claim is UNSUPPORTED.
Do not use outside knowledge.

JSON Schema required:
{
    "claims": [
        {
            "claim_id": "C1",
            "text": "The refund period is 30 days.",
            "status": "supported" | "unsupported",
            "reason": "Explain why based on context",
            "source_chunk_ids": ["S1"] 
        }
    ]
}

Return ONLY valid JSON. No markdown backticks.
"""
        
        user_prompt = f"""
EVIDENCE CONTEXT:
{context_str}

GENERATED ANSWER:
{answer}

Analyze the groundedness of the generated answer.
"""
        try:
            raw_response = await self.llm.generate(system_prompt, user_prompt)
            # Clean possible markdown formatting from LLM
            clean_json = raw_response.strip().removeprefix("```json").removesuffix("```").strip()
            
            data = json.loads(clean_json)
            
            claims_data = data.get("claims", [])
            total = len(claims_data)
            supported = sum(1 for c in claims_data if c.get("status") == "supported")
            
            return GroundednessResult(
                supported_claims=supported,
                total_claims=total,
                claims=claims_data
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Groundedness LLM returned invalid JSON: {e}\nRaw: {raw_response}")
            return GroundednessResult(supported_claims=0, total_claims=0, claims=[{"error": "Failed to parse LLM evaluation"}])
        except Exception as e:
            logger.error(f"Groundedness check failed: {e}")
            return GroundednessResult(supported_claims=0, total_claims=0, claims=[{"error": str(e)}])
