from typing import List, Dict, Any, Tuple
from app.core.storage import VectorStorage, SparseIndex
from app.services.embeddings import EmbeddingService
from app.services.reranker import CrossEncoderReranker
from app.schemas.domain import RetrievedChunk, Chunk
from app.core.storage import RelationalStorage
import asyncio
import time

class RetrievalPipeline:
    def __init__(self, 
                 vector_storage: VectorStorage, 
                 sparse_index: SparseIndex, 
                 embedding_service: EmbeddingService,
                 reranker: CrossEncoderReranker,
                 relational_storage: RelationalStorage):
        self.vector_storage = vector_storage
        self.sparse_index = sparse_index
        self.embedding_service = embedding_service
        self.reranker = reranker
        self.relational_storage = relational_storage
        
    async def retrieve(self, query: str, bm25_k: int = 20, dense_k: int = 20, rrf_k: int = 60, top_k: int = 5) -> Tuple[List[RetrievedChunk], Dict[str, Any]]:
        trace_data = {}
        
        # 1. Embed query
        start_t = time.perf_counter()
        query_embedding = self.embedding_service.encode([query])[0]
        trace_data['embedding_ms'] = (time.perf_counter() - start_t) * 1000
        
        # 2. Parallel retrieval
        start_t = time.perf_counter()
        bm25_task = self.sparse_index.search(query, top_k=bm25_k)
        dense_task = self.vector_storage.search(query_embedding, top_k=dense_k)
        
        bm25_results, dense_results = await asyncio.gather(bm25_task, dense_task)
        trace_data['bm25_ms'] = (time.perf_counter() - start_t) * 1000 # Approximation
        trace_data['dense_retrieval_ms'] = trace_data['bm25_ms']
        
        # 3. RRF (Reciprocal Rank Fusion)
        start_t = time.perf_counter()
        fused_scores = {}
        
        def add_to_rrf(results, weight=1.0):
            for rank, res in enumerate(results):
                chunk_id = res['chunk_id']
                score = weight / (rrf_k + rank + 1)
                fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + score
                
        add_to_rrf(bm25_results)
        add_to_rrf(dense_results)
        
        sorted_fused = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        # Take union candidate set (e.g. top 20 from RRF)
        candidate_ids = [x[0] for x in sorted_fused[:max(bm25_k, dense_k)]]
        trace_data['rrf_ms'] = (time.perf_counter() - start_t) * 1000
        
        # 4. Fetch candidate chunks
        candidate_chunks = []
        for cid in candidate_ids:
            chunk = await self.relational_storage.get_chunk(cid)
            if chunk:
                candidate_chunks.append(chunk)
                
        if not candidate_chunks:
            return [], trace_data
            
        # 5. Reranking
        start_t = time.perf_counter()
        texts_to_rerank = [c.text for c in candidate_chunks]
        rerank_scores = self.reranker.rerank(query, texts_to_rerank)
        
        # Combine chunks with scores
        scored_candidates = list(zip(candidate_chunks, rerank_scores))
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        trace_data['reranking_ms'] = (time.perf_counter() - start_t) * 1000
        
        # 6. Format output
        final_results = []
        for rank, (chunk, score) in enumerate(scored_candidates[:top_k]):
            final_results.append(RetrievedChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                provenance=chunk.provenance,
                score=score,
                rank=rank + 1,
                retrieval_method="hybrid_rrf_cross_encoder"
            ))
            
        return final_results, trace_data
