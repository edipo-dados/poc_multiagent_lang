"""
Generate embeddings and save to SQL file.
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.embeddings import EmbeddingService


def generate_embeddings():
    """Generate embeddings and create SQL insert statements."""
    print("Gerando embeddings...")
    print()
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    
    # Files to embed
    repo_path = Path("fake_pix_repo")
    files_to_embed = [
        "api/endpoints.py",
        "api/schemas.py",
        "domain/models.py",
        "domain/validators.py",
        "database/models.py",
    ]
    
    sql_statements = []
    
    for file_path in files_to_embed:
        full_path = repo_path / file_path
        if not full_path.exists():
            print(f"  ⚠️  Arquivo não encontrado: {file_path}")
            continue
        
        print(f"  Processando: {file_path}")
        
        # Read file content
        content = full_path.read_text(encoding='utf-8')
        
        # Generate embedding
        embedding = embedding_service.encode(content)
        
        # Escape content for SQL
        content_escaped = content.replace("'", "''")
        
        # Convert embedding to PostgreSQL array format
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        
        # Create SQL statement
        sql = f"""
INSERT INTO embeddings (file_path, content, embedding)
VALUES ('{file_path}', '{content_escaped}', '{embedding_str}'::vector)
ON CONFLICT (file_path) 
DO UPDATE SET 
    content = EXCLUDED.content,
    embedding = EXCLUDED.embedding,
    updated_at = NOW();
"""
        sql_statements.append(sql)
        print(f"    ✓ Embedding gerado ({len(embedding)} dimensões)")
    
    # Save to file
    output_file = Path("insert_embeddings.sql")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print()
    print(f"✓ SQL gerado em: {output_file}")
    print(f"✓ Total de arquivos: {len(sql_statements)}")
    print()
    print("Execute:")
    print(f"  docker exec -i multi-agent-ia-postgres-1 psql -U postgres -d regulatory_ai < {output_file}")


if __name__ == "__main__":
    generate_embeddings()
