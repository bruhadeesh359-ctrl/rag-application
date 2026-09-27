import time
from typing import List
from app.schemas.domain import RetrievedChunk, Chunk
from app.core.storage import VectorStorage, SparseIndex, RelationalStorage
from app.services.embeddings import EmbeddingService

class DenseRetriever:
    def __init__(self, vector_storage: VectorStorage, embedding_service: EmbeddingService, relational_storage: RelationalStorage):
        self.vector_storage = vector_storage
        self.embedding_service = embedding_service
        self.relational_storage = relational_storage

    async def retrieve(self, query: str, top_k: int = 10) -> dict:
        start_t = time.perf_counter()
        
        # 1. Embed query
        query_embedding = self.embedding_service.embed_text(query)
        
        # 2. Search Vector Storage
        search_results = await self.vector_storage.search(query_embedding, top_k)
        
        # 3. Reconstruct full chunks via relational DB to preserve exact provenance
        final_results = []
        rank = 1
        for res in search_results:
            chunk = await self.relational_storage.get_chunk(res["chunk_id"])
            if chunk:
                final_results.append(RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    provenance=chunk.provenance,
                    score=res["score"],
                    rank=rank,
                    retrieval_method="dense"
                ))
                rank += 1
                
        latency_ms = (time.perf_counter() - start_t) * 1000
        
        # Output structured dict compatible with API expectations
        return {
            "query": query,
            "retrieval_method": "dense",
            "results": final_results,
            "latency_ms": round(latency_ms, 2)
        }


class SparseRetriever:
    def __init__(self, sparse_index: SparseIndex, relational_storage: RelationalStorage):
        self.sparse_index = sparse_index
        self.relational_storage = relational_storage

    async def retrieve(self, query: str, top_k: int = 10) -> dict:
        start_t = time.perf_counter()
        
        search_results = await self.sparse_index.search(query, top_k)
        
        final_results = []
        rank = 1
        for res in search_results:
            chunk = await self.relational_storage.get_chunk(res["chunk_id"])
            if chunk:
                final_results.append(RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    provenance=chunk.provenance,
                    score=res["score"],
                    rank=rank,
                    retrieval_method="bm25"
                ))
                rank += 1
                
        latency_ms = (time.perf_counter() - start_t) * 1000
        
        return {
            "query": query,
            "retrieval_method": "bm25",
            "results": final_results,
            "latency_ms": round(latency_ms, 2)
        }
