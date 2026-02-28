-- Create embeddings table
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(512) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
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
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_file_path ON embeddings(file_path);
CREATE INDEX IF NOT EXISTS idx_audit_execution_id ON audit_logs(execution_id);
CREATE INDEX IF NOT EXISTS idx_audit_risk_level ON audit_logs(risk_level);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
