import pytest
from app.services.context_builder import ContextBuilder
from app.schemas.domain import RetrievedChunk, Provenance

def create_mock_chunk(chunk_id: str, doc_name: str, page: int, text: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=doc_name.split('.')[0],
        text=text,
        provenance=Provenance(
            document_id=doc_name.split('.')[0],
            filename=doc_name,
            page=page,
            chunk_index=0
        ),
        score=0.9,
        rank=1,
        retrieval_method="hybrid"
    )

def test_context_builder_mapping():
    builder = ContextBuilder(max_context_chunks=5)
    
    chunks = [
        create_mock_chunk("c1", "docA.pdf", 1, "Content A"),
        create_mock_chunk("c2", "docB.pdf", 5, "Content B"),
    ]
    
    context_str, citation_map = builder.build_context(chunks)
    
    assert "S1" in citation_map
    assert "S2" in citation_map
    assert citation_map["S1"].chunk_id == "c1"
    assert citation_map["S2"].chunk_id == "c2"
    
    assert "[S1]" in context_str
    assert "docA.pdf" in context_str
    assert "Content A" in context_str
    
    assert "[S2]" in context_str
    assert "docB.pdf" in context_str
    assert "Content B" in context_str

def test_context_builder_truncation():
    builder = ContextBuilder(max_context_chunks=2)
    
    chunks = [
        create_mock_chunk("c1", "docA.pdf", 1, "Content A"),
        create_mock_chunk("c2", "docB.pdf", 5, "Content B"),
        create_mock_chunk("c3", "docC.pdf", 2, "Content C"),
    ]
    
    context_str, citation_map = builder.build_context(chunks)
    
    assert len(citation_map) == 2
    assert "S1" in citation_map
    assert "S2" in citation_map
    assert "S3" not in citation_map
    
    assert "Content C" not in context_str
