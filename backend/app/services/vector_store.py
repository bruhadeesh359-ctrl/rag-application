import chromadb
from typing import List, Dict, Any
from app.core.storage import VectorStorage
from app.schemas.domain import ChunkCreate
import os

class ChromaVectorStorage(VectorStorage):
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            data_dir = os.getenv("DATA_DIR", ".")
            persist_directory = os.path.join(data_dir, "chroma_db")
            
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="rag_chunks",
            metadata={"hnsw:space": "cosine"}
        )

    async def add_embeddings(self, chunks: List[ChunkCreate], embeddings: List[List[float]]):
        if not chunks:
            return
            
        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = []
        for c in chunks:
            # Flatten provenance for metadata
            meta = {
                "document_id": c.provenance.document_id,
                "filename": c.provenance.filename,
                "chunk_index": c.provenance.chunk_index
            }
            metadatas.append(meta)
            
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    async def search(self, query_embedding: List[float], top_k: int) -> List[dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        matches = []
        if results['ids'] and len(results['ids']) > 0:
            for idx, chunk_id in enumerate(results['ids'][0]):
                # chroma returns distance, we convert to similarity (approx)
                distance = results['distances'][0][idx] if 'distances' in results and results['distances'] else 0
                similarity = 1.0 - distance # valid for cosine distance
                
                matches.append({
                    "chunk_id": chunk_id,
                    "score": similarity
                })
                
        return matches
