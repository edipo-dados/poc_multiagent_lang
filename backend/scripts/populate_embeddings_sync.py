"""
Populate embeddings using synchronous psycopg2.
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load .env
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

from backend.services.embeddings import EmbeddingService


def populate_embeddings():
    """Populate embeddings for fake_pix_repo."""
    print("Populando embeddings para fake_pix_repo...")
    print()
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="regulatory_ai",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    
    # Files to embed
    repo_path = Path("fake_pix_repo")
    files_to_embed = [
        "api/endpoints.py",
        "api/schemas.py",
        "domain/models.py",
        "domain/validators.py",
        "database/models.py",
    ]
    
    for file_path in files_to_embed:
        full_path = repo_path / file_path
        if not full_path.exists():
            print(f"  ⚠️  Arquivo não encontrado: {file_path}")
            continue
        
        print(f"  Processando: {file_path}")
        
        # Read file content
        content = full_path.read_text(encoding='utf-8')
        
        # Generate embedding
        print(f"    Gerando embedding...")
        embedding = embedding_service.encode(content)
        
        # Convert embedding to PostgreSQL array format
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        
        # Upsert into database
        print(f"    Salvando no banco...")
        cur.execute("""
            INSERT INTO embeddings (file_path, content, embedding)
            VALUES (%s, %s, %s::vector)
            ON CONFLICT (file_path) 
            DO UPDATE SET 
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                updated_at = NOW()
        """, (file_path, content, embedding_str))
        
        conn.commit()
        print(f"    ✓ Concluído ({len(embedding)} dimensões)")
        print()
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM embeddings")
    count = cur.fetchone()[0]
    print(f"✓ Total de embeddings no banco: {count}")
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    populate_embeddings()
