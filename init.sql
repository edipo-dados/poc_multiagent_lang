-- Database initialization script for regulatory-ai-poc
-- Creates tables for embeddings and audit logs with pgvector support

CREATE EXTENSION IF NOT EXISTS vector;

-- Embeddings table for storing code file vector representations
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(512) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create IVFFlat index for fast cosine similarity search
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Audit logs table for storing complete execution history
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL UNIQUE,
    raw_text TEXT NOT NULL,
    change_detected BOOLEAN,
    risk_level VARCHAR(10),
    structured_model JSONB,
    impacted_files JSONB,
    impact_analysis JSONB,
    technical_spec TEXT,
    kiro_prompt TEXT,
    error TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient audit log queries
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_risk_level ON audit_logs(risk_level);
