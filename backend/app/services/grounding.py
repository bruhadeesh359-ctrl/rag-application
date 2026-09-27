from typing import List, Dict, Any, Tuple
import re
import time
from app.schemas.domain import RetrievedChunk, GroundednessResult, ExtractedClaim
from app.services.llm_provider import LLMProvider

class GroundingService:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def extract_claims(self, answer: str) -> List[ExtractedClaim]:
        # Using LLM to extract discrete claims from the generated answer
        system_prompt = "Extract discrete, verifiable factual claims from the text. Return as a bulleted list."
        # Mocking for now to save tokens
        return [
            ExtractedClaim(claim_id="claim_1", text="Mocked claim 1", source_chunk_ids=["chunk_1"]),
            ExtractedClaim(claim_id="claim_2", text="Mocked claim 2", source_chunk_ids=["chunk_2"])
        ]

    async def verify_claims(self, claims: List[ExtractedClaim], chunks: List[RetrievedChunk]) -> Tuple[GroundednessResult, float]:
        start_t = time.perf_counter()
        
        # In reality, you'd iterate over claims and ask an LLM or NLI model 
        # whether the chunk entails the claim.
        
        supported = 0
        total = len(claims)
        claim_results = []
        
        for claim in claims:
            # Mock verification
            status = "supported" # or "unsupported"
            if status == "supported":
                supported += 1
            claim_results.append({
                "claim_id": claim.claim_id,
                "text": claim.text,
                "status": status,
                "reason": "Mocked validation: The claim is supported by the context."
            })
            
        validation_ms = (time.perf_counter() - start_t) * 1000
        
        result = GroundednessResult(
            supported_claims=supported,
            total_claims=total,
            claims=claim_results
        )
        return result, validation_ms
