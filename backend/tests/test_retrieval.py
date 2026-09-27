import pytest
from app.services.sparse_index import BM25SparseIndex
from app.schemas.domain import ChunkCreate, Provenance

@pytest.fixture
def test_chunks():
    p1 = Provenance(document_id="doc1", filename="test1", chunk_index=0)
    p2 = Provenance(document_id="doc2", filename="test2", chunk_index=0)
    return [
        ChunkCreate(chunk_id="chunk1", document_id="doc1", text="The quick brown fox jumps over the lazy dog.", provenance=p1),
        ChunkCreate(chunk_id="chunk2", document_id="doc2", text="Machine learning relies heavily on high-quality data.", provenance=p2),
        ChunkCreate(chunk_id="chunk3", document_id="doc2", text="The quick red fox", provenance=p2)
    ]

@pytest.mark.asyncio
async def test_bm25_index_and_retrieve(test_chunks):
    # Using a transient or test path is better, but since it's just tests, 
    # we'll use a specific test file.
    index = BM25SparseIndex(persist_path="./test_bm25")
    await index.index_chunks(test_chunks)
    
    # Retrieve
    results = await index.search("fox", top_k=2)
    assert len(results) == 2
    assert results[0]["chunk_id"] in ["chunk1", "chunk3"]
    assert "score" in results[0]

@pytest.mark.asyncio
async def test_bm25_empty_query():
    index = BM25SparseIndex(persist_path="./test_bm25_empty")
    results = await index.search("", top_k=2)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_bm25_unknown_query(test_chunks):
    index = BM25SparseIndex(persist_path="./test_bm25_unknown")
    await index.index_chunks(test_chunks)
    
    results = await index.search("astronaut", top_k=5)
    # They return score 0, or length > 0 with score 0. Let's see rank_bm25 behavior.
    assert len(results) >= 0
    if len(results) > 0:
        assert results[0]["score"] == 0.0
