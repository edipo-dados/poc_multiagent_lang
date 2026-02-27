"""
SQLAlchemy ORM models for database tables.

This module defines the database schema for:
- Embeddings: Vector embeddings of code files for semantic search
- AuditLog: Complete execution history for compliance tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class Embedding(Base):
    """
    Stores vector embeddings of code files for semantic search.
    
    Uses pgvector extension for efficient cosine similarity search.
    Embedding dimension is 384 (sentence-transformers/all-MiniLM-L6-v2).
    """
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String(512), nullable=False, unique=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    """
    Stores complete execution history for compliance and debugging.
    
    Each analysis execution creates one audit log entry with all inputs,
    intermediate results, and final outputs stored as JSONB.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(36), nullable=False, unique=True, index=True)
    raw_text = Column(Text, nullable=False)
    change_detected = Column(Boolean, nullable=True)
    risk_level = Column(String(10), nullable=True, index=True)
    structured_model = Column(JSONB, nullable=True)
    impacted_files = Column(JSONB, nullable=True)
    impact_analysis = Column(JSONB, nullable=True)
    technical_spec = Column(Text, nullable=True)
    kiro_prompt = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)
