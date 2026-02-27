"""
Vector Store Service for semantic code search.

Provides methods for storing and searching code embeddings using
PostgreSQL with pgvector extension for cosine similarity search.

Requirements: 11.4, 11.5
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql import func
from backend.database.models import Embedding
from backend.models.impact import ImpactedFile


class VectorStoreService:
    """
    Service for managing vector embeddings and semantic search.
    
    Uses pgvector extension for efficient cosine similarity search
    on code file embeddings.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize vector store service with database session.
        
        Args:
            session: Async SQLAlchemy session for database operations
        """
        self.session = session
    
    async def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        threshold: float = 0.5
    ) -> list[ImpactedFile]:
        """
        Search for similar code files using cosine similarity.
        
        Uses pgvector's cosine distance operator to find files with
        embeddings most similar to the query embedding. Results are
        ordered by relevance score (1 - cosine_distance) in descending order.
        
        Args:
            query_embedding: Vector embedding of search query (384 dimensions)
            top_k: Maximum number of results to return (default: 10)
            threshold: Minimum relevance score (0.0 to 1.0, default: 0.5)
        
        Returns:
            List of ImpactedFile objects with file_path, relevance_score, and snippet
            
        Requirements: 11.5
        """
        # Calculate cosine similarity (1 - cosine_distance)
        # pgvector's cosine_distance returns 0 for identical vectors, 2 for opposite
        similarity = 1 - Embedding.embedding.cosine_distance(query_embedding)
        
        # Build query with similarity filter and ordering
        stmt = (
            select(
                Embedding.file_path,
                Embedding.content,
                similarity.label('score')
            )
            .where(similarity >= threshold)
            .order_by(similarity.desc())
            .limit(top_k)
        )
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        # Convert to ImpactedFile objects
        return [
            ImpactedFile(
                file_path=row.file_path,
                relevance_score=float(row.score),
                snippet=row.content[:200]  # First 200 chars as preview
            )
            for row in rows
        ]
    
    async def upsert_embedding(
        self,
        file_path: str,
        content: str,
        embedding: list[float]
    ) -> None:
        """
        Insert or update file embedding in vector store.
        
        If a file with the same path already exists, updates its content
        and embedding. Otherwise, creates a new entry. Uses PostgreSQL's
        ON CONFLICT clause for atomic upsert operation.
        
        Args:
            file_path: Relative path to file in repository
            content: Full text content of the file
            embedding: Vector embedding of the file content (384 dimensions)
            
        Requirements: 11.4
        """
        # Use PostgreSQL's INSERT ... ON CONFLICT for atomic upsert
        stmt = pg_insert(Embedding).values(
            file_path=file_path,
            content=content,
            embedding=embedding
        )
        
        # On conflict (duplicate file_path), update content and embedding
        stmt = stmt.on_conflict_do_update(
            index_elements=['file_path'],
            set_={
                'content': content,
                'embedding': embedding,
                'updated_at': func.now()
            }
        )
        
        await self.session.execute(stmt)
        await self.session.commit()
    
    async def get_embedding_count(self) -> int:
        """
        Get total number of embeddings in vector store.
        
        Returns:
            Count of embedding records
        """
        stmt = select(func.count()).select_from(Embedding)
        result = await self.session.execute(stmt)
        return result.scalar_one()
    
    async def get_embedding(self, file_path: str) -> Optional[Embedding]:
        """
        Retrieve embedding record for a specific file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Embedding object if found, None otherwise
        """
        stmt = select(Embedding).where(Embedding.file_path == file_path)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
