from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.domain import DocumentCreate, ChunkCreate, Chunk

class RelationalStorage(ABC):
    @abstractmethod
    async def save_document(self, document: DocumentCreate):
        pass

    @abstractmethod
    async def save_chunks(self, chunks: List[ChunkCreate]):
        pass
        
    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[DocumentCreate]:
        pass

    @abstractmethod
    async def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        pass

    @abstractmethod
    async def save_trace(self, trace_obj):
        pass

class VectorStorage(ABC):
    @abstractmethod
    async def add_embeddings(self, chunks: List[ChunkCreate], embeddings: List[List[float]]):
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float], top_k: int) -> List[dict]:
        """Returns list of dicts with chunk_id and similarity score"""
        pass

class SparseIndex(ABC):
    @abstractmethod
    async def index_chunks(self, chunks: List[ChunkCreate]):
        pass

    @abstractmethod
    async def search(self, query: str, top_k: int) -> List[dict]:
        """Returns list of dicts with chunk_id and bm25 score"""
        pass
