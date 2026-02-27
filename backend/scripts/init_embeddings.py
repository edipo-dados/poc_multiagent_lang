"""
Repository Embedding Initialization Script.

Generates and stores embeddings for all Python files in the fake Pix repository.
This script should be run once during system setup to populate the vector store.

Requirements: 11.1, 11.4
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import AsyncSessionLocal
from services.embeddings import EmbeddingService
from services.vector_store import VectorStoreService


async def initialize_embeddings(repo_path: str = "fake_pix_repo") -> None:
    """
    Generate and store embeddings for all Python files in repository.
    
    Iterates through all .py files in the specified repository path,
    generates embeddings using the EmbeddingService, and stores them
    in the vector store for semantic search.
    
    Args:
        repo_path: Path to repository root (default: "fake_pix_repo")
        
    Requirements: 11.1, 11.4
    """
    # Resolve repository path relative to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    repo_full_path = project_root / repo_path
    
    if not repo_full_path.exists():
        print(f"Error: Repository path not found: {repo_full_path}")
        sys.exit(1)
    
    print(f"Initializing embeddings for repository: {repo_full_path}")
    
    # Initialize services
    embedding_service = EmbeddingService()
    print(f"Loaded embedding model: {embedding_service.model_name}")
    print(f"Embedding dimension: {embedding_service.get_dimension()}")
    
    # Find all Python files
    python_files = list(repo_full_path.rglob("*.py"))
    print(f"\nFound {len(python_files)} Python files")
    
    if len(python_files) == 0:
        print("Warning: No Python files found in repository")
        return
    
    # Read file contents
    file_data = []
    for file_path in python_files:
        try:
            content = file_path.read_text(encoding='utf-8')
            relative_path = str(file_path.relative_to(project_root))
            file_data.append((relative_path, content))
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
    
    print(f"Successfully read {len(file_data)} files")
    
    # Generate embeddings in batch for efficiency
    print("\nGenerating embeddings...")
    texts = [content for _, content in file_data]
    embeddings = embedding_service.encode_batch(texts)
    print(f"Generated {len(embeddings)} embeddings")
    
    # Store embeddings in database
    print("\nStoring embeddings in vector store...")
    async with AsyncSessionLocal() as session:
        vector_store = VectorStoreService(session)
        
        for (file_path, content), embedding in zip(file_data, embeddings):
            await vector_store.upsert_embedding(
                file_path=file_path,
                content=content,
                embedding=embedding
            )
            print(f"  ✓ {file_path}")
        
        # Verify count
        total_count = await vector_store.get_embedding_count()
        print(f"\nTotal embeddings in vector store: {total_count}")
    
    print("\n✅ Embedding initialization complete!")


async def verify_embeddings() -> None:
    """
    Verify that embeddings are stored correctly in vector store.
    
    Performs a simple test query to ensure the vector store is working.
    """
    print("\n--- Verification ---")
    
    embedding_service = EmbeddingService()
    
    # Test query
    test_query = "Pix transaction validation"
    query_embedding = embedding_service.encode(test_query)
    
    async with AsyncSessionLocal() as session:
        vector_store = VectorStoreService(session)
        
        # Search for similar files
        results = await vector_store.search_similar(
            query_embedding=query_embedding,
            top_k=5,
            threshold=0.0  # Low threshold to get any results
        )
        
        print(f"\nTest query: '{test_query}'")
        print(f"Found {len(results)} similar files:")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.file_path}")
            print(f"   Relevance: {result.relevance_score:.3f}")
            print(f"   Snippet: {result.snippet[:100]}...")


def main():
    """
    Main entry point for embedding initialization script.
    
    Usage:
        python backend/scripts/init_embeddings.py
    """
    # Get repository path from environment or use default
    repo_path = os.getenv("PIX_REPO_PATH", "fake_pix_repo")
    
    # Run initialization
    asyncio.run(initialize_embeddings(repo_path))
    
    # Run verification
    asyncio.run(verify_embeddings())


if __name__ == "__main__":
    main()
