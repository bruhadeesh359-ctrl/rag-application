from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import os
import uuid
import time
import tempfile
from typing import Dict, Any

from app.schemas.api import APIResponse
from app.schemas.domain import DocumentCreate, DocumentMetadata, ChunkCreate
from app.api.dependencies import get_relational_storage, get_vector_storage, get_sparse_index, get_embedding_service
from app.services.document_parser import DocumentParser
from app.services.chunker import Chunker

router = APIRouter()

@router.post("/ingest", response_model=APIResponse[Dict[str, Any]])
async def ingest_document(
    file: UploadFile = File(...),
    relational_storage = Depends(get_relational_storage),
    vector_storage = Depends(get_vector_storage),
    sparse_index = Depends(get_sparse_index),
    embedding_service = Depends(get_embedding_service)
):
    start_time = time.time()
    temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}_{file.filename}")
    
    # Save uploaded file to temporary path
    try:
        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)
            
        # Parse document
        try:
            raw_content = DocumentParser.parse_file(temp_path)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        document_id = str(uuid.uuid4())
        import datetime
        doc_metadata = DocumentMetadata(
            filename=file.filename,
            file_type=file.content_type or "application/octet-stream",
            file_size_bytes=len(contents),
            created_at=datetime.datetime.utcnow().isoformat() + "Z"
        )
        
        doc_create = DocumentCreate(
            document_id=document_id,
            metadata=doc_metadata,
            raw_content=raw_content
        )
        
        # Save original document to SQL
        await relational_storage.save_document(doc_create)
        
        from app.services.chunker import FixedSizeChunker
        # Chunk document
        chunker_instance = FixedSizeChunker()
        chunks = chunker_instance.chunk_document(doc_create)
        if not chunks:
            return APIResponse(
                data={
                    "document_id": document_id,
                    "filename": file.filename,
                    "status": "success",
                    "chunk_count": 0,
                    "duration_ms": int((time.time() - start_time) * 1000)
                }
            )
            
        # Extract embeddings
        texts = [c.text for c in chunks]
        embeddings = embedding_service.embed_texts(texts)
        
        # Save chunks
        await relational_storage.save_chunks(chunks)
        await vector_storage.add_embeddings(chunks, embeddings)
        await sparse_index.index_chunks(chunks)
        
        return APIResponse(
            data={
                "document_id": document_id,
                "filename": file.filename,
                "status": "success",
                "chunk_count": len(chunks),
                "duration_ms": int((time.time() - start_time) * 1000)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
