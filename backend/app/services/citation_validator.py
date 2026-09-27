import re
from typing import Dict, List, Set, Any
from app.schemas.domain import RetrievedChunk
import logging

logger = logging.getLogger(__name__)

class CitationValidator:
    """
    Parses LLM-generated answers for [Sx] citation tokens, and validates 
    them against the ContextBuilder's map.
    """
    
    # Regex to find citations like [S1], [S2], [S10]
    CITATION_PATTERN = re.compile(r'\[S(\d+)\]')

    def validate(self, generated_answer: str, citation_map: Dict[str, RetrievedChunk]) -> Dict[str, Any]:
        """
        Validates the presence and correctness of citations in the generated answer.
        Returns a dictionary containing validation metadata.
        """
        # Find all unique citation strings, e.g., ["S1", "S2"]
        extracted_citations: Set[str] = {f"S{match}" for match in self.CITATION_PATTERN.findall(generated_answer)}
        
        valid_citations = []
        invalid_citations = []
        
        for cit in extracted_citations:
            if cit in citation_map:
                valid_citations.append(cit)
            else:
                invalid_citations.append(cit)
                
        # Are there citations that the LLM hallucinated?
        has_invalid = len(invalid_citations) > 0
        
        # Did the LLM cite anything at all?
        has_citations = len(extracted_citations) > 0
        
        result = {
            "is_valid": not has_invalid,
            "has_citations": has_citations,
            "extracted_citations": list(extracted_citations),
            "valid_citations": valid_citations,
            "invalid_citations": invalid_citations,
            "mapped_chunks": [citation_map[c].chunk_id for c in valid_citations]
        }
        
        if has_invalid:
            logger.warning(f"Invalid citations detected: {invalid_citations}")
            
        return result
