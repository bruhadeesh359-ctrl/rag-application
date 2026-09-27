import torch
import logging
from typing import List, Optional
from app.schemas.domain import RetrievedChunk
from app.core.config import settings

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    """
    Reranks a list of candidate chunks against a query using a Cross-Encoder.
    """
    def __init__(self):
        self.enabled = settings.retrieval.reranker.enabled
        self.model_name = settings.retrieval.reranker.model
        self.batch_size = settings.retrieval.reranker.batch_size
        self.device = self._determine_device(settings.retrieval.reranker.device)
        self.model = None

    def _determine_device(self, config_device: str) -> str:
        if config_device == "auto":
            if torch.cuda.is_available():
                # For RTX 3050 6GB, we might want to check memory, but CrossEncoder is usually 
                # ~1GB for MiniLM, so it should fit if not heavily loaded.
                return "cuda"
            return "cpu"
        return config_device
        
    def _load_model(self):
        if not self.model:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading CrossEncoder: {self.model_name} on {self.device}")
            self.model = CrossEncoder(self.model_name, device=self.device)
            
    def rerank(self, query: str, candidates: List[RetrievedChunk], top_k: Optional[int] = None) -> List[RetrievedChunk]:
        """
        Reranks candidates. Modifies the score and rank, sets retrieval_method to 'cross-encoder'.
        Preserves provenance.
        """
        if not self.enabled or not candidates:
            return candidates[:top_k] if top_k else candidates
            
        try:
            self._load_model()
        except Exception as e:
            logger.error(f"Failed to load CrossEncoder model. Falling back to input ranking. Error: {e}")
            return candidates[:top_k] if top_k else candidates

        # Prepare pairs: (query, document_text)
        model_inputs = [[query, chunk.text] for chunk in candidates]
        
        try:
            # Predict scores
            scores = self.model.predict(model_inputs, batch_size=self.batch_size)
        except Exception as e:
            logger.error(f"Error during CrossEncoder prediction: {e}")
            return candidates[:top_k] if top_k else candidates
            
        # Combine chunks with new scores
        scored_candidates = list(zip(candidates, scores))
        
        # Sort descending by cross-encoder score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        limit = top_k if top_k is not None else settings.retrieval.final_top_k
        
        final_results = []
        for new_rank, (original_chunk, score) in enumerate(scored_candidates[:limit], start=1):
            reranked_chunk = RetrievedChunk(
                chunk_id=original_chunk.chunk_id,
                document_id=original_chunk.document_id,
                text=original_chunk.text,
                provenance=original_chunk.provenance,
                score=float(score), 
                rank=new_rank,
                retrieval_method="cross-encoder",
                original_rank=original_chunk.original_rank or original_chunk.rank,
                rrf_score=original_chunk.rrf_score,
                reranker_score=float(score),
                final_rank=new_rank
            )
            final_results.append(reranked_chunk)
            
        return final_results
