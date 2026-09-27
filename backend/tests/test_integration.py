import pytest
import pytest_asyncio
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.sql_models import Base
from app.services.sqlite_storage import SQLiteStorage
from app.services.vector_store import ChromaVectorStorage
from app.services.sparse_index import BM25SparseIndex
from app.services.embeddings import EmbeddingService
from app.services.chunker import FixedSizeChunker
from app.services.retrievers import DenseRetriever, SparseRetriever
from app.schemas.domain import DocumentCreate, DocumentMetadata

@pytest_asyncio.fixture
async def setup_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_full_pipeline_integration(setup_db):
    session = setup_db
    
    # 1. Init Services
    relational_storage = SQLiteStorage(session)
    vector_storage = ChromaVectorStorage("./test_chroma")
    sparse_index = BM25SparseIndex("./test_bm25")
    embedding_service = EmbeddingService()
    chunker = FixedSizeChunker(chunk_size=50)
    
    # 2. Create Document
    doc = DocumentCreate(
        document_id="integration_doc_1",
        metadata=DocumentMetadata(
            filename="integration.txt",
            file_type="txt",
            file_size_bytes=100,
            created_at="2023-01-01T00:00:00"
        ),
        raw_content="The new product launch resulted in a 25% increase in revenue for Q3. We anticipate this trend continuing into Q4."
    )
    
    # 3. Parse/Chunk
    await relational_storage.save_document(doc)
    chunks = chunker.chunk_document(doc)
    await relational_storage.save_chunks(chunks)
    
    assert len(chunks) > 0
    assert chunks[0].provenance.document_id == "integration_doc_1"
    
    # 4. Embed and Index Vector Storage
    embeddings = embedding_service.embed_chunks(chunks)
    await vector_storage.add_embeddings(chunks, embeddings)
    
    # 5. Index Sparse
    await sparse_index.index_chunks(chunks)
    
    # 6. Retrieve
    dense_retriever = DenseRetriever(vector_storage, embedding_service, relational_storage)
    sparse_retriever = SparseRetriever(sparse_index, relational_storage)
    
    dense_results = await dense_retriever.retrieve("revenue increase", top_k=2)
    bm25_results = await sparse_retriever.retrieve("revenue Q3", top_k=2)
    
    # 7. Assertions
    assert dense_results["retrieval_method"] == "dense"
    assert bm25_results["retrieval_method"] == "bm25"
    
    assert len(dense_results["results"]) > 0
    assert len(bm25_results["results"]) > 0
    
    # Assert structured schema
    first_res = dense_results["results"][0]
    assert first_res.chunk_id.startswith("integration_doc_1")
    assert first_res.score > 0
    assert first_res.rank == 1
    assert first_res.provenance.filename == "integration.txt"
