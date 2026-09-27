from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_embedding_service, get_reranker_service

client = TestClient(app)

class MockEmbeddingService:
    def get_model_name(self):
        return "mock-embedding-model"

class MockRerankerConfig:
    name_or_path = "mock-reranker-model"

class MockRerankerModel:
    config = MockRerankerConfig()

class MockRerankerService:
    model = MockRerankerModel()

app.dependency_overrides[get_embedding_service] = MockEmbeddingService
app.dependency_overrides[get_reranker_service] = MockRerankerService

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "ok"
    assert data["data"]["service"] == "rag-platform"

def test_system_info():
    response = client.get("/api/v1/system")
    assert response.status_code == 200
    data = response.json()
    
    assert data["data"]["status"] == "READY"
    assert data["data"]["models"]["embedding_model"] == "mock-embedding-model"
    assert data["data"]["models"]["reranker_model"] == "mock-reranker-model"
    assert "os" in data["data"]["runtime"]
    assert "python_version" in data["data"]["runtime"]
