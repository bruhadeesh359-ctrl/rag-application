import torch
from sentence_transformers import SentenceTransformer
from typing import List
import time

class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: str = "auto", batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        
        # Determine optimal device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        elif device == "cuda" and not torch.cuda.is_available():
            # Fallback for safety
            self.device = "cpu"
        else:
            self.device = device
            
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
        except Exception as e:
            # Fallback to cpu if CUDA OOM on init
            if self.device == "cuda":
                self.device = "cpu"
                self.model = SentenceTransformer(self.model_name, device=self.device)
            else:
                raise e

        # Extract dimension
        self.dimension = self.model.get_sentence_embedding_dimension()

    def get_dimension(self) -> int:
        return self.dimension

    def get_model_name(self) -> str:
        return self.model_name

    def embed_text(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
            
        try:
            # Normalize embeddings to match semantic requirements
            embeddings = self.model.encode(texts, batch_size=self.batch_size, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.tolist()
        except torch.cuda.OutOfMemoryError:
            # Safe CPU fallback if CUDA OOM happens during encoding
            if self.device == "cuda":
                self.model.cpu()
                self.device = "cpu"
                embeddings = self.model.encode(texts, batch_size=self.batch_size, convert_to_numpy=True, normalize_embeddings=True)
                return embeddings.tolist()
            raise

    def embed_chunks(self, chunks: list) -> List[List[float]]:
        texts = [c.text for c in chunks]
        return self.embed_texts(texts)
