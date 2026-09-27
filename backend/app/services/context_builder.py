from typing import List, Dict, Tuple
from app.schemas.domain import RetrievedChunk
import logging

logger = logging.getLogger(__name__)

class ContextBuilder:
    """
    Takes retrieved chunks and prepares them safely for the LLM context.
    Assigns stable source identifiers (e.g., [S1], [S2]) to preserve provenance.
    """
    def __init__(self, max_context_chunks: int = 5):
        self.max_context_chunks = max_context_chunks

    def build_context(self, chunks: List[RetrievedChunk]) -> Tuple[str, Dict[str, RetrievedChunk]]:
        """
        Takes the ranked chunks, assigns [S1]..[Sn] identifiers, 
        and returns the formatted string alongside the mapping dictionary.
        
        It preserves the input order (which should be the final reranked order).
        """
        # Respect context bounds
        truncated_chunks = chunks[:self.max_context_chunks]
        
        if len(truncated_chunks) < len(chunks):
            logger.info(f"Context Builder truncated {len(chunks)} chunks to {self.max_context_chunks}")
            
        context_string_parts = []
        citation_map = {}
        
        for index, chunk in enumerate(truncated_chunks):
            citation_id = f"S{index + 1}"
            citation_map[citation_id] = chunk
            
            # Formulate the chunk representation
            # We explicitly include provenance data as text so the LLM knows *where* it came from
            prov = chunk.provenance
            
            chunk_repr = (
                f"[{citation_id}]\n"
                f"Document: {prov.filename}\n"
            )
            if prov.page is not None:
                chunk_repr += f"Page: {prov.page}\n"
            if prov.section is not None:
                chunk_repr += f"Section: {prov.section}\n"
                
            chunk_repr += f"Text:\n{chunk.text}\n"
            context_string_parts.append(chunk_repr)
            
        final_context_string = "\n".join(context_string_parts)
        return final_context_string, citation_map
