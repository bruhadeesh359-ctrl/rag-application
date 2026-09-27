from sqlalchemy import Column, String, Integer, Text, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class SQLDocument(Base):
    __tablename__ = 'documents'
    
    document_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    created_at = Column(String, nullable=False)
    additional_info = Column(JSON, default={})
    raw_content = Column(Text, nullable=False)
    
    chunks = relationship("SQLChunk", back_populates="document", cascade="all, delete-orphan")

class SQLChunk(Base):
    __tablename__ = 'chunks'
    
    chunk_id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey('documents.document_id'), nullable=False)
    text = Column(Text, nullable=False)
    
    # Provenance fields
    page = Column(Integer, nullable=True)
    section = Column(String, nullable=True)
    chunk_index = Column(Integer, nullable=False)
    source_location = Column(String, nullable=True)
    
    document = relationship("SQLDocument", back_populates="chunks")

class SQLExperiment(Base):
    __tablename__ = 'experiments'
    
    experiment_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
class SQLTrace(Base):
    __tablename__ = 'traces'
    
    trace_id = Column(String, primary_key=True, index=True)
    request_id = Column(String, index=True, nullable=True)
    experiment_id = Column(String, index=True, nullable=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="running")
    
    # Token & Cost 
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    token_source = Column(String, nullable=True)
    input_cost = Column(Float, nullable=True)
    output_cost = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    
    # Relationships
    spans = relationship("SQLSpan", back_populates="trace", cascade="all, delete-orphan")
    errors = relationship("SQLErrorEvent", back_populates="trace", cascade="all, delete-orphan")

class SQLSpan(Base):
    __tablename__ = 'spans'
    
    span_id = Column(String, primary_key=True, index=True)
    trace_id = Column(String, ForeignKey('traces.trace_id'), nullable=False, index=True)
    parent_span_id = Column(String, nullable=True, index=True)
    stage = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="running")
    attributes = Column(JSON, default={})
    
    trace = relationship("SQLTrace", back_populates="spans")

class SQLErrorEvent(Base):
    __tablename__ = 'error_events'
    
    error_id = Column(String, primary_key=True, index=True)
    trace_id = Column(String, ForeignKey('traces.trace_id'), nullable=False, index=True)
    span_id = Column(String, nullable=True, index=True)
    category = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    retryable = Column(Integer, default=0) # boolean via integer
    component = Column(String, nullable=False)
    
    trace = relationship("SQLTrace", back_populates="errors")
