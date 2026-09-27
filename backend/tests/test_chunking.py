import pytest
from app.services.chunker import FixedSizeChunker
from app.schemas.domain import DocumentCreate, DocumentMetadata

@pytest.fixture
def chunker():
    return FixedSizeChunker(chunk_size=10, overlap=3)

def create_mock_doc(content: str) -> DocumentCreate:
    return DocumentCreate(
        document_id="doc1",
        metadata=DocumentMetadata(
            filename="test.txt",
            file_type="text/plain",
            file_size_bytes=len(content),
            created_at="2023-01-01T00:00:00",
            additional_info={"page": 1, "section": "intro"}
        ),
        raw_content=content
    )

def test_empty_document(chunker):
    doc = create_mock_doc("")
    chunks = chunker.chunk_document(doc)
    assert len(chunks) == 0

def test_whitespace_only_document(chunker):
    doc = create_mock_doc("   \n \t ")
    chunks = chunker.chunk_document(doc)
    assert len(chunks) == 0

def test_short_document(chunker):
    doc = create_mock_doc("hello world")
    chunks = chunker.chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0].text == "hello world"
    assert chunks[0].chunk_id == "doc1_chunk_000"

def test_chunking_overlap(chunker):
    doc = create_mock_doc("one two three four five six seven eight nine ten")
    chunks = chunker.chunk_document(doc)
    
    assert len(chunks) > 1
    
    # Assert deterministic provenance and IDs
    assert chunks[0].provenance.document_id == "doc1"
    assert chunks[0].provenance.page == 1
    assert chunks[0].provenance.chunk_index == 0
    assert chunks[1].chunk_id == "doc1_chunk_001"

def test_metadata_preservation(chunker):
    doc = create_mock_doc("Some content")
    chunks = chunker.chunk_document(doc)
    assert chunks[0].provenance.filename == "test.txt"
    assert chunks[0].provenance.section == "intro"
    assert chunks[0].provenance.page == 1
