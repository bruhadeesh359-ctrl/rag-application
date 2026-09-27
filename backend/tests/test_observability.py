import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.tracer import tracer
from app.services.hybrid_retriever import HybridRetriever
from app.services.rag_service import RAGService
from app.schemas.domain import RetrievedChunk, Provenance
from app.core.llm import GeminiProvider
from app.schemas.observability import TokenUsage

@pytest.fixture
def mock_retriever():
    sparse_retriever = AsyncMock()
    dense_retriever = AsyncMock()
    
    # Mocking basic chunks
    chunk = RetrievedChunk(
        chunk_id="test_1",
        document_id="doc_1",
        text="Test evidence text.",
        score=0.9,
        rank=1,
        retrieval_method="mock",
        provenance=Provenance(document_id="doc_1", filename="test.pdf", page=1, chunk_index=0)
    )
    
    
    sparse_retriever.retrieve.return_value = [chunk]
    dense_retriever.retrieve.return_value = [chunk]
    
    hybrid = HybridRetriever(sparse_retriever, dense_retriever)
    hybrid.reranker = MagicMock()
    hybrid.reranker.rerank.return_value = [chunk]
    return hybrid

@pytest.fixture
def rag_service(mock_retriever):
    with patch('app.services.rag_service.get_llm_provider') as mock_get_llm:
        mock_llm = AsyncMock(spec=GeminiProvider)
        mock_llm.generate.return_value = "This is a response [S1]."
        mock_llm.last_token_usage = {"input_tokens": 50, "output_tokens": 10, "total_tokens": 60}
        mock_get_llm.return_value = mock_llm
        
        service = RAGService(mock_retriever)
        return service

@pytest.mark.asyncio
async def test_trace_hierarchy_generation(rag_service):
    # Mock the save_trace to intercept the trace before it's thrown away
    with patch('app.core.tracer.tracer.storage') as mock_storage:
        mock_storage.save_trace = AsyncMock()
        
        result = await rag_service.query("What is testing?")
        
        # Verify trace was saved
        assert mock_storage.save_trace.called
        trace = mock_storage.save_trace.call_args[0][0]
        
        assert trace.status == "grounded"
        assert trace.token_usage.total_tokens == 60
        assert trace.token_usage.input_tokens == 50
        
        # Check spans
        spans = trace.spans
        # Expected spans: context_building, llm_generation, validation, retrieval_pipeline, base_retrieval, rrf_fusion, reranking
        span_stages = [s.stage for s in spans]
        assert "context_building" in span_stages
        assert "llm_generation" in span_stages
        assert "validation" in span_stages
        assert "retrieval_pipeline" in span_stages
        
        # Check parent/child relationship
        retrieval_span = next(s for s in spans if s.stage == "retrieval_pipeline")
        base_retrieval_span = next(s for s in spans if s.stage == "base_retrieval")
        
        assert base_retrieval_span.parent_span_id == retrieval_span.span_id
        
        assert trace.duration_ms >= 0
        assert base_retrieval_span.duration_ms >= 0

@pytest.mark.asyncio
async def test_trace_abstained_on_insufficient_evidence(rag_service):
    # Modify retriever to return low scores
    rag_service.retriever.reranker.rerank.return_value[0].score = 0.001
    
    with patch('app.core.tracer.tracer.storage') as mock_storage:
        mock_storage.save_trace = AsyncMock()
        
        result = await rag_service.query("What is testing?")
        
        assert result["status"] == "abstained"
        
        trace = mock_storage.save_trace.call_args[0][0]
        assert trace.status == "abstained"
        assert len(trace.errors) == 1
        assert trace.errors[0].category == "INSUFFICIENT_EVIDENCE"
        assert trace.errors[0].severity == "INFO"

@pytest.mark.asyncio
async def test_trace_error_logging_on_llm_failure(rag_service):
    rag_service.llm.generate.side_effect = Exception("API limit reached")
    
    with patch('app.core.tracer.tracer.storage') as mock_storage:
        mock_storage.save_trace = AsyncMock()
        
        result = await rag_service.query("What is testing?")
        
        trace = mock_storage.save_trace.call_args[0][0]
        assert trace.status == "error"
        assert len(trace.errors) == 1
        assert trace.errors[0].category == "LLM_GENERATION_ERROR"
        assert "API limit reached" in trace.errors[0].message
        
        # Verify LLM generation span also got marked with error
        llm_span = next(s for s in trace.spans if s.stage == "llm_generation")
        assert llm_span.status == "error"
