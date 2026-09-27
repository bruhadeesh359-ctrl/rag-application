import pytest
from app.services.citation_validator import CitationValidator
from app.schemas.domain import RetrievedChunk, Provenance

def test_citation_validator_valid():
    validator = CitationValidator()
    
    citation_map = {
        "S1": RetrievedChunk(chunk_id="c1", document_id="d1", text="", provenance=Provenance(document_id="d1", filename="d1.pdf", chunk_index=0), score=1, rank=1, retrieval_method="rrf"),
        "S2": RetrievedChunk(chunk_id="c2", document_id="d2", text="", provenance=Provenance(document_id="d2", filename="d2.pdf", chunk_index=0), score=1, rank=2, retrieval_method="rrf")
    }
    
    answer = "The policy states 30 days [S1]. The refund is processed quickly [S2]."
    
    result = validator.validate(answer, citation_map)
    
    assert result["is_valid"] is True
    assert result["has_citations"] is True
    assert set(result["valid_citations"]) == {"S1", "S2"}
    assert result["invalid_citations"] == []
    assert set(result["mapped_chunks"]) == {"c1", "c2"}

def test_citation_validator_invalid_hallucinated():
    validator = CitationValidator()
    
    citation_map = {
        "S1": RetrievedChunk(chunk_id="c1", document_id="d1", text="", provenance=Provenance(document_id="d1", filename="d1.pdf", chunk_index=0), score=1, rank=1, retrieval_method="rrf"),
    }
    
    # S99 is a hallucinated citation
    answer = "The policy states 30 days [S1]. The secret password is password123 [S99]."
    
    result = validator.validate(answer, citation_map)
    
    assert result["is_valid"] is False
    assert result["has_citations"] is True
    assert set(result["valid_citations"]) == {"S1"}
    assert set(result["invalid_citations"]) == {"S99"}

def test_citation_validator_no_citations():
    validator = CitationValidator()
    
    citation_map = {
        "S1": RetrievedChunk(chunk_id="c1", document_id="d1", text="", provenance=Provenance(document_id="d1", filename="d1.pdf", chunk_index=0), score=1, rank=1, retrieval_method="rrf"),
    }
    
    answer = "I'm not sure, the text doesn't say."
    
    result = validator.validate(answer, citation_map)
    
    assert result["is_valid"] is True # Technically valid because it didn't fake any
    assert result["has_citations"] is False
    assert result["valid_citations"] == []
    assert result["invalid_citations"] == []
