import pytest
from app.services.embeddings import EmbeddingService

@pytest.fixture
def embedding_service():
    # Will use CPU or CUDA based on availability, baseline tests must work
    return EmbeddingService(model_name="sentence-transformers/all-MiniLM-L6-v2")

def test_model_initialization(embedding_service):
    assert embedding_service.get_model_name() == "sentence-transformers/all-MiniLM-L6-v2"
    assert embedding_service.get_dimension() == 384
    assert embedding_service.device in ["cpu", "cuda"]

def test_single_text_embedding(embedding_service):
    emb = embedding_service.embed_text("hello world")
    assert len(emb) == 384
    assert isinstance(emb[0], float)

def test_batch_embedding(embedding_service):
    texts = ["hello", "world", "this is a test"]
    embs = embedding_service.embed_texts(texts)
    assert len(embs) == 3
    assert len(embs[0]) == 384

def test_empty_input(embedding_service):
    embs = embedding_service.embed_texts([])
    assert embs == []
