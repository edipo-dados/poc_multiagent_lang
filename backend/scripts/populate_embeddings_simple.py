"""
Populate embeddings for fake_pix_repo files.
"""

import asyncio
import os
import sys
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

from backend.database.connection import AsyncSessionLocal
from backend.services.embeddings import EmbeddingService
from backend.services.vector_store import VectorStoreService


async def populate_embeddings():
    """Populate embeddings for fake_pix_repo."""
    print("Populando embeddings para fake_pix_repo...")
    print()
    
    # Initialize services
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
    
    async with AsyncSessionLocal() as session:
        vector_store = VectorStoreService(session)
        
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
            
            # Store in vector store
            print(f"    Salvando no banco...")
            await vector_store.upsert_embedding(
                file_path=file_path,
                content=content,
                embedding=embedding
            )
            
            print(f"    ✓ Concluído ({len(embedding)} dimensões)")
            print()
        
        # Verify
        count = await vector_store.get_embedding_count()
        print(f"✓ Total de embeddings no banco: {count}")


if __name__ == "__main__":
    asyncio.run(populate_embeddings())
