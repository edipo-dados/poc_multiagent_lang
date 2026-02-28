"""
Initialize embeddings for SQLite database with fake_pix_repo files.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database.connection import AsyncSessionLocal
from backend.services.embeddings import EmbeddingService
from backend.services.vector_store import VectorStoreService


async def initialize_embeddings():
    """Initialize embeddings for fake_pix_repo."""
    print("Initializing embeddings for fake_pix_repo...")
    
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
                print(f"  ⚠️  File not found: {file_path}")
                continue
            
            print(f"  Processing: {file_path}")
            
            # Read file content
            content = full_path.read_text(encoding='utf-8')
            
            # Generate embedding
            embedding = embedding_service.encode(content)
            
            # Store in vector store
            await vector_store.upsert_embedding(
                file_path=file_path,
                content=content,
                embedding=embedding
            )
            
            print(f"    ✓ Embedded ({len(embedding)} dimensions)")
        
        # Verify
        count = await vector_store.get_embedding_count()
        print(f"\n✓ Total embeddings in database: {count}")


if __name__ == "__main__":
    asyncio.run(initialize_embeddings())
