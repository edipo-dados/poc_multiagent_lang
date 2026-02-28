"""
Populate embeddings using asyncpg (already installed in production).
"""

import os
import sys
import asyncio
from pathlib import Path

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
import asyncpg


async def populate_embeddings():
    """Populate embeddings for fake_pix_repo."""
    print("🔄 Populando embeddings para fake_pix_repo...")
    print()
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    
    # Connect to PostgreSQL using asyncpg
    db_host = os.getenv("DB_HOST", "postgres")
    conn = await asyncpg.connect(
        host=db_host,
        port=5432,
        database="regulatory_ai",
        user="postgres",
        password="postgres"
    )
    
    try:
        # Files to embed
        repo_base = os.getenv("PIX_REPO_PATH", "fake_pix_repo")
        repo_path = Path(repo_base)
        
        if not repo_path.exists():
            print(f"❌ Erro: Repositório não encontrado em {repo_path}")
            print(f"   Verifique se o volume está montado corretamente")
            return
        
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
            
            print(f"  📄 Processando: {file_path}")
            
            # Read file content
            content = full_path.read_text(encoding='utf-8')
            
            # Generate embedding
            print(f"    🔢 Gerando embedding...")
            embedding = embedding_service.encode(content)
            
            # Convert embedding to list for asyncpg
            embedding_list = embedding.tolist()
            
            # Upsert into database
            print(f"    💾 Salvando no banco...")
            await conn.execute("""
                INSERT INTO code_embeddings (file_path, content, embedding)
                VALUES ($1, $2, $3::vector)
                ON CONFLICT (file_path) 
                DO UPDATE SET 
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    updated_at = NOW()
            """, file_path, content, embedding_list)
            
            print(f"    ✅ Concluído ({len(embedding)} dimensões)")
            print()
        
        # Verify
        count = await conn.fetchval("SELECT COUNT(*) FROM code_embeddings")
        print(f"✅ Total de embeddings no banco: {count}")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(populate_embeddings())
