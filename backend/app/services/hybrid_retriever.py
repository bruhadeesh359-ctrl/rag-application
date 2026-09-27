import time
import asyncio
from typing import List, Dict, Any, Tuple
from app.schemas.domain import RetrievedChunk
from app.services.retrievers import DenseRetriever, SparseRetriever
from app.services.fusion import RRFFusion
from app.services.reranker import CrossEncoderReranker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class HybridRetriever:
    """
    Orchestrates the entire Phase 3 Hybrid Retrieval Pipeline:
    BM25 + Dense -> RRF Fusion -> CrossEncoder Reranking
    """
    def __init__(
        self, 
        sparse_retriever: SparseRetriever, 
        dense_retriever: DenseRetriever,
        fusion_service: RRFFusion = None,
        reranker_service: CrossEncoderReranker = None
    ):
        self.sparse_retriever = sparse_retriever
        self.dense_retriever = dense_retriever
        self.fusion = fusion_service or RRFFusion()
        self.reranker = reranker_service or CrossEncoderReranker()

    async def retrieve(self, query: str) -> List[RetrievedChunk]:
        """
        Executes the full pipeline and returns the final ranked candidates.
        """
        if not query.strip():
            return []
            
        # 1. Parallel execution of BM25 and Dense
        bm25_top_k = settings.retrieval.bm25_top_k
        dense_top_k = settings.retrieval.dense_top_k
        
        from app.core.tracer import tracer
        
        retrieval_span = tracer.start_span("retrieval_pipeline")
        
        base_span = tracer.start_span("base_retrieval")
        bm25_task = self.sparse_retriever.retrieve(query, top_k=bm25_top_k)
        dense_task = self.dense_retriever.retrieve(query, top_k=dense_top_k)
        
        try:
            sparse_results, dense_results = await asyncio.gather(bm25_task, dense_task)
            tracer.end_span(base_span)
        except Exception as e:
            tracer.record_error("RETRIEVAL_ERROR", str(e), component="base_retrieval")
            tracer.end_span(base_span, status="error")
            tracer.end_span(retrieval_span, status="error")
            logger.error(f"Error during parallel retrieval: {e}")
            raise

        # 2. RRF Fusion
        rrf_span = tracer.start_span("rrf_fusion")
        sparse_chunks = sparse_results.get("results", [])
        dense_chunks = dense_results.get("results", [])
        fused_candidates = self.fusion.fuse(sparse_chunks, dense_chunks, top_k=settings.retrieval.fusion_top_k)
        tracer.end_span(rrf_span, attributes={"candidate_count": len(fused_candidates)})
        
        # 3. CrossEncoder Reranking
        rerank_span = tracer.start_span("reranking")
        final_results = self.reranker.rerank(query, fused_candidates, top_k=settings.retrieval.final_top_k)
        tracer.end_span(rerank_span, attributes={"final_count": len(final_results)})
        
        tracer.end_span(retrieval_span)
        return final_results

    async def retrieve_with_inspector(self, query: str) -> Dict[str, Any]:
        """
        Executes the full pipeline and captures detailed stage metrics and timing 
        for observability and debugging (Phase 3 Inspector).
        """
        if not query.strip():
            raise ValueError("Query cannot be empty")
            
        timings = {}
        t0 = time.perf_counter()
        
        # 1. Base Retrieval
        bm25_top_k = settings.retrieval.bm25_top_k
        dense_top_k = settings.retrieval.dense_top_k
        
        t_base_start = time.perf_counter()
        bm25_task = self.sparse_retriever.retrieve(query, top_k=bm25_top_k)
        dense_task = self.dense_retriever.retrieve(query, top_k=dense_top_k)
        
        sparse_results, dense_results = await asyncio.gather(bm25_task, dense_task)
        t_base_end = time.perf_counter()
        
        # For detailed timings, we can't easily split asyncio parallel wait without instrumenting the inner methods, 
        # so we record parallel execution time as base_retrieval_ms
        timings["base_retrieval_ms"] = (t_base_end - t_base_start) * 1000

        # 2. RRF Fusion
        t_rrf_start = time.perf_counter()
        sparse_chunks = sparse_results.get("results", [])
        dense_chunks = dense_results.get("results", [])
        fused_candidates = self.fusion.fuse(sparse_chunks, dense_chunks, top_k=settings.retrieval.fusion_top_k)
        t_rrf_end = time.perf_counter()
        timings["rrf_ms"] = (t_rrf_end - t_rrf_start) * 1000

        # 3. Reranking
        t_rerank_start = time.perf_counter()
        final_results = self.reranker.rerank(query, fused_candidates, top_k=settings.retrieval.final_top_k)
        t_rerank_end = time.perf_counter()
        timings["reranker_ms"] = (t_rerank_end - t_rerank_start) * 1000
        
        timings["total_ms"] = (time.perf_counter() - t0) * 1000

        # Construct Inspector Response
        return {
            "query": query,
            "bm25_results": sparse_results,
            "dense_results": dense_results,
            "rrf_results": fused_candidates,
            "reranked_results": final_results,
            "timings": timings,
            "config_used": {
                "bm25_top_k": bm25_top_k,
                "dense_top_k": dense_top_k,
                "fusion_top_k": settings.retrieval.fusion_top_k,
                "final_top_k": settings.retrieval.final_top_k,
                "rrf_enabled": self.fusion.enabled,
                "reranker_enabled": self.reranker.enabled,
                "reranker_model": self.reranker.model_name
            }
        }
