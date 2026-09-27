from rank_bm25 import BM25Okapi
import json
import os
from typing import List, Dict, Any
from app.core.storage import SparseIndex
from app.schemas.domain import ChunkCreate

class BM25SparseIndex(SparseIndex):
    def __init__(self, persist_path: str = "./bm25_index"):
        self.persist_path = persist_path
        self.corpus = []
        self.chunk_ids = []
        self.bm25 = None
        self._load()

    def _tokenize(self, text: str) -> List[str]:
        # Simple whitespace tokenizer. 
        # In production, use standard NLP tokenization.
        return text.lower().split()

    def _load(self):
        if os.path.exists(f"{self.persist_path}.json"):
            with open(f"{self.persist_path}.json", "r") as f:
                data = json.load(f)
                self.corpus = data.get("corpus", [])
                self.chunk_ids = data.get("chunk_ids", [])
                if self.corpus:
                    tokenized_corpus = [self._tokenize(doc) for doc in self.corpus]
                    self.bm25 = BM25Okapi(tokenized_corpus)

    def _save(self):
        with open(f"{self.persist_path}.json", "w") as f:
            json.dump({
                "corpus": self.corpus,
                "chunk_ids": self.chunk_ids
            }, f)

    async def index_chunks(self, chunks: List[ChunkCreate]):
        for c in chunks:
            self.corpus.append(c.text)
            self.chunk_ids.append(c.chunk_id)
            
        if self.corpus:
            tokenized_corpus = [self._tokenize(doc) for doc in self.corpus]
            self.bm25 = BM25Okapi(tokenized_corpus)
            self._save()

    async def search(self, query: str, top_k: int) -> List[dict]:
        if not self.bm25:
            return []
            
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Zip with IDs and sort
        scored_results = list(zip(self.chunk_ids, scores))
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        matches = []
        # Normalizing BM25 score to 0-1 range is tricky, we return raw score
        # but in RRF this won't matter as RRF uses rank.
        for chunk_id, score in scored_results[:top_k]:
            matches.append({
                "chunk_id": chunk_id,
                "score": score
            })
            
        return matches
