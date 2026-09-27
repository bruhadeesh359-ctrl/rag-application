from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
import json

from app.core.storage import RelationalStorage
from app.schemas.domain import DocumentCreate, ChunkCreate, Chunk, Provenance, DocumentMetadata
from app.models.sql_models import SQLDocument, SQLChunk

class SQLiteStorage(RelationalStorage):
    def __init__(self):
        from app.core.database import async_session
        self.session_maker = async_session

    async def save_document(self, document: DocumentCreate):
        async with self.session_maker() as session:
            sql_doc = SQLDocument(
                document_id=document.document_id,
                filename=document.metadata.filename,
                file_type=document.metadata.file_type,
                file_size_bytes=document.metadata.file_size_bytes,
                created_at=document.metadata.created_at,
                additional_info=document.metadata.additional_info,
                raw_content=document.raw_content
            )
            session.add(sql_doc)
            await session.commit()

    async def save_chunks(self, chunks: List[ChunkCreate]):
        async with self.session_maker() as session:
            for c in chunks:
                sql_chunk = SQLChunk(
                    chunk_id=c.chunk_id,
                    document_id=c.document_id,
                    text=c.text,
                    page=c.provenance.page,
                    section=c.provenance.section,
                    chunk_index=c.provenance.chunk_index,
                    source_location=c.provenance.source_location
                )
                session.add(sql_chunk)
            await session.commit()

    async def get_document(self, document_id: str) -> Optional[DocumentCreate]:
        async with self.session_maker() as session:
            result = await session.execute(select(SQLDocument).filter(SQLDocument.document_id == document_id))
            doc = result.scalars().first()
            if not doc:
                return None
                
            return DocumentCreate(
                document_id=doc.document_id,
                metadata=DocumentMetadata(
                    filename=doc.filename,
                    file_type=doc.file_type,
                    file_size_bytes=doc.file_size_bytes,
                    created_at=doc.created_at,
                    additional_info=doc.additional_info
                ),
                raw_content=doc.raw_content
            )

    async def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        async with self.session_maker() as session:
            stmt = select(SQLChunk).options(joinedload(SQLChunk.document)).filter(SQLChunk.chunk_id == chunk_id)
            result = await session.execute(stmt)
            chunk = result.scalars().first()
            if not chunk:
                return None
                
            return Chunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                provenance=Provenance(
                    document_id=chunk.document_id,
                    filename=chunk.document.filename,
                    page=chunk.page,
                    section=chunk.section,
                    chunk_index=chunk.chunk_index,
                    source_location=chunk.source_location
                )
            )

    async def count_documents(self) -> int:
        async with self.session_maker() as session:
            result = await session.execute(select(SQLDocument))
            return len(result.scalars().all())

    async def count_chunks(self) -> int:
        async with self.session_maker() as session:
            result = await session.execute(select(SQLChunk))
            return len(result.scalars().all())

    async def save_trace(self, trace_obj):
        from app.models.sql_models import SQLTrace, SQLSpan, SQLErrorEvent
        
        async with self.session_maker() as session:
            sql_trace = SQLTrace(
                trace_id=trace_obj.trace_id,
                request_id=trace_obj.request_id,
                experiment_id=trace_obj.experiment_id,
                start_time=trace_obj.start_time,
                end_time=trace_obj.end_time,
                duration_ms=trace_obj.duration_ms,
                status=trace_obj.status
            )
            
            if trace_obj.token_usage:
                sql_trace.input_tokens = trace_obj.token_usage.input_tokens
                sql_trace.output_tokens = trace_obj.token_usage.output_tokens
                sql_trace.total_tokens = trace_obj.token_usage.total_tokens
                sql_trace.token_source = trace_obj.token_usage.token_source
                
            if trace_obj.cost:
                sql_trace.input_cost = trace_obj.cost.input_cost
                sql_trace.output_cost = trace_obj.cost.output_cost
                sql_trace.total_cost = trace_obj.cost.total_cost
                sql_trace.currency = trace_obj.cost.currency
                
            for span in trace_obj.spans:
                sql_span = SQLSpan(
                    span_id=span.span_id,
                    trace_id=span.trace_id,
                    parent_span_id=span.parent_span_id,
                    stage=span.stage,
                    start_time=span.start_time,
                    end_time=span.end_time,
                    duration_ms=span.duration_ms,
                    status=span.status,
                    attributes=span.attributes
                )
                sql_trace.spans.append(sql_span)
                
            for error in trace_obj.errors:
                sql_error = SQLErrorEvent(
                    error_id=error.error_id,
                    trace_id=error.trace_id,
                    span_id=error.span_id,
                    category=error.category,
                    severity=error.severity,
                    message=error.message,
                    timestamp=error.timestamp,
                    retryable=1 if error.retryable else 0,
                    component=error.component
                )
                sql_trace.errors.append(sql_error)
                
            session.add(sql_trace)
            await session.commit()
