from typing import List, Dict, Any, Optional
from app.schemas.domain import RetrievedChunk
from app.core.config import settings
import uuid

class RRFFusion:
    """
    Implements Reciprocal Rank Fusion (RRF) for combining multiple ranked lists.
    RRF_score(d) = Σ 1 / (k + rank_i(d))
    """
    def __init__(self):
        self.k = settings.retrieval.rrf.k
        self.enabled = settings.retrieval.rrf.enabled
        self.bm25_weight = settings.retrieval.rrf.bm25_weight
        self.dense_weight = settings.retrieval.rrf.dense_weight

    def fuse(
        self, 
        sparse_results: List[RetrievedChunk], 
        dense_results: List[RetrievedChunk], 
        top_k: Optional[int] = None
    ) -> List[RetrievedChunk]:
        """
        Fuses sparse (BM25) and dense results using RRF.
        Returns a newly ranked list of RetrievedChunk objects.
        """
        if not self.enabled:
            # If disabled, just return dense results (or a simple combination)
            # as a fallback. But standard is to run RRF.
            return dense_results
            
        chunk_map: Dict[str, RetrievedChunk] = {}
        score_map: Dict[str, float] = {}
        
        # Process Sparse Results
        for chunk in sparse_results:
            chunk_id = chunk.chunk_id
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = chunk
                score_map[chunk_id] = 0.0
            
            # Use its actual rank, 1-indexed
            rank = chunk.rank if chunk.rank > 0 else 1
            rrf_score = 1.0 / (self.k + rank)
            score_map[chunk_id] += (rrf_score * self.bm25_weight)
            
        # Process Dense Results
        for chunk in dense_results:
            chunk_id = chunk.chunk_id
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = chunk
                score_map[chunk_id] = 0.0
                
            rank = chunk.rank if chunk.rank > 0 else 1
            rrf_score = 1.0 / (self.k + rank)
            score_map[chunk_id] += (rrf_score * self.dense_weight)
            
        # Sort by accumulated RRF score descending
        sorted_chunks = sorted(score_map.items(), key=lambda item: item[1], reverse=True)
        
        # Limit to top_k if specified, else use configured fusion_top_k
        limit = top_k if top_k is not None else settings.retrieval.fusion_top_k
        
        fused_results = []
        for new_rank, (chunk_id, rrf_score) in enumerate(sorted_chunks[:limit], start=1):
            original_chunk = chunk_map[chunk_id]
            
            # Create a new RetrievedChunk to avoid mutating the original
            # and to properly track provenance and fusion stage
            fused_chunk = RetrievedChunk(
                chunk_id=original_chunk.chunk_id,
                document_id=original_chunk.document_id,
                text=original_chunk.text,
                provenance=original_chunk.provenance,
                score=rrf_score, # Make primary score the RRF score
                rank=new_rank,   # Make primary rank the fusion rank
                retrieval_method="rrf",
                original_rank=original_chunk.rank, # Just track one of the original ranks for reference
                rrf_score=rrf_score
            )
            fused_results.append(fused_chunk)
            
        return fused_results
