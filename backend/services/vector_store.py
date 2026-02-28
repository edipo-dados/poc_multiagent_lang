"""
Vector Store Service for semantic code search.

Provides methods for storing and searching code embeddings using
PostgreSQL with pgvector extension for cosine similarity search.
Falls back to Python-based cosine similarity for SQLite.

Requirements: 11.4, 11.5
"""

import json
import math
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, text
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
        # Detect database type from environment or session
        import os
        database_url = os.getenv("DATABASE_URL", "")
        self.is_sqlite = 'sqlite' in database_url.lower()
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"VectorStoreService initialized - is_sqlite: {self.is_sqlite}, DATABASE_URL: {database_url[:50]}...")
    
    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        threshold: float = 0.5
    ) -> list[ImpactedFile]:
        """
        Search for similar code files using cosine similarity.
        
        Uses pgvector's cosine distance operator for PostgreSQL or
        Python-based cosine similarity for SQLite. Results are
        ordered by relevance score in descending order.
        
        Args:
            query_embedding: Vector embedding of search query (384 dimensions)
            top_k: Maximum number of results to return (default: 10)
            threshold: Minimum relevance score (0.0 to 1.0, default: 0.5)
        
        Returns:
            List of ImpactedFile objects with file_path, relevance_score, and snippet
            
        Requirements: 11.5
        """
        if self.is_sqlite:
            return await self._search_similar_sqlite(query_embedding, top_k, threshold)
        else:
            return await self._search_similar_postgres(query_embedding, top_k, threshold)
    
    async def _search_similar_postgres(
        self,
        query_embedding: list[float],
        top_k: int,
        threshold: float
    ) -> list[ImpactedFile]:
        """PostgreSQL implementation using pgvector."""
        # Calculate cosine similarity (1 - cosine_distance)
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
                snippet=row.content[:200]
            )
            for row in rows
        ]
    
    async def _search_similar_sqlite(
        self,
        query_embedding: list[float],
        top_k: int,
        threshold: float
    ) -> list[ImpactedFile]:
        """SQLite implementation using Python-based cosine similarity."""
        # Fetch all embeddings (SQLite doesn't have vector operations)
        stmt = select(Embedding.file_path, Embedding.content, Embedding.embedding)
        result = await self.session.execute(stmt)
        rows = result.all()
        
        # Calculate similarity in Python
        results = []
        for row in rows:
            # Parse embedding from JSON string if needed
            if isinstance(row.embedding, str):
                embedding = json.loads(row.embedding)
            else:
                embedding = row.embedding
            
            similarity = self._cosine_similarity(query_embedding, embedding)
            
            if similarity >= threshold:
                results.append({
                    'file_path': row.file_path,
                    'content': row.content,
                    'score': similarity
                })
        
        # Sort by score descending and limit
        results.sort(key=lambda x: x['score'], reverse=True)
        results = results[:top_k]
        
        # Convert to ImpactedFile objects
        return [
            ImpactedFile(
                file_path=r['file_path'],
                relevance_score=r['score'],
                snippet=r['content'][:200]
            )
            for r in results
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
        and embedding. Otherwise, creates a new entry.
        
        Args:
            file_path: Relative path to file in repository
            content: Full text content of the file
            embedding: Vector embedding of the file content (384 dimensions)
            
        Requirements: 11.4
        """
        if self.is_sqlite:
            await self._upsert_embedding_sqlite(file_path, content, embedding)
        else:
            await self._upsert_embedding_postgres(file_path, content, embedding)
    
    async def _upsert_embedding_postgres(
        self,
        file_path: str,
        content: str,
        embedding: list[float]
    ) -> None:
        """PostgreSQL implementation using ON CONFLICT."""
        stmt = pg_insert(Embedding).values(
            file_path=file_path,
            content=content,
            embedding=embedding
        )
        
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
    
    async def _upsert_embedding_sqlite(
        self,
        file_path: str,
        content: str,
        embedding: list[float]
    ) -> None:
        """SQLite implementation using INSERT OR REPLACE."""
        # Check if exists
        existing = await self.get_embedding(file_path)
        
        # For SQLite, store embedding as JSON string
        embedding_json = json.dumps(embedding)
        
        if existing:
            # Update
            stmt = (
                Embedding.__table__.update()
                .where(Embedding.file_path == file_path)
                .values(content=content, embedding=embedding_json)
            )
        else:
            # Insert
            stmt = Embedding.__table__.insert().values(
                file_path=file_path,
                content=content,
                embedding=embedding_json
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
