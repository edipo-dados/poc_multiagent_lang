"""
Unit tests for Vector Store Service.

Tests embedding storage, retrieval, and semantic search functionality.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from backend.database.models import Base, Embedding
from backend.services.vector_store import VectorStoreService
from backend.models.impact import ImpactedFile


# Test database URL (in-memory or test database)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/regulatory_ai_test"


@pytest.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def session(test_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_upsert_embedding_creates_new(session):
    """Test that upsert_embedding creates a new embedding record."""
    vector_store = VectorStoreService(session)
    
    # Create test embedding
    test_embedding = [0.1] * 384  # 384-dimensional vector
    
    await vector_store.upsert_embedding(
        file_path="test/file.py",
        content="def test(): pass",
        embedding=test_embedding
    )
    
    # Verify it was created
    result = await vector_store.get_embedding("test/file.py")
    assert result is not None
    assert result.file_path == "test/file.py"
    assert result.content == "def test(): pass"


@pytest.mark.asyncio
async def test_upsert_embedding_updates_existing(session):
    """Test that upsert_embedding updates an existing record."""
    vector_store = VectorStoreService(session)
    
    # Create initial embedding
    test_embedding = [0.1] * 384
    await vector_store.upsert_embedding(
        file_path="test/file.py",
        content="def test(): pass",
        embedding=test_embedding
    )
    
    # Update with new content
    new_embedding = [0.2] * 384
    await vector_store.upsert_embedding(
        file_path="test/file.py",
        content="def test_updated(): pass",
        embedding=new_embedding
    )
    
    # Verify it was updated
    result = await vector_store.get_embedding("test/file.py")
    assert result is not None
    assert result.content == "def test_updated(): pass"
    
    # Verify only one record exists
    count = await vector_store.get_embedding_count()
    assert count == 1


@pytest.mark.asyncio
async def test_search_similar_returns_ordered_results(session):
    """Test that search_similar returns results ordered by relevance."""
    vector_store = VectorStoreService(session)
    
    # Create embeddings with different similarities
    # Embedding 1: Very similar to query
    similar_embedding = [1.0, 0.0] + [0.0] * 382
    await vector_store.upsert_embedding(
        file_path="similar.py",
        content="Very similar content",
        embedding=similar_embedding
    )
    
    # Embedding 2: Less similar to query
    less_similar_embedding = [0.5, 0.5] + [0.0] * 382
    await vector_store.upsert_embedding(
        file_path="less_similar.py",
        content="Less similar content",
        embedding=less_similar_embedding
    )
    
    # Embedding 3: Not similar to query
    dissimilar_embedding = [0.0, 1.0] + [0.0] * 382
    await vector_store.upsert_embedding(
        file_path="dissimilar.py",
        content="Dissimilar content",
        embedding=dissimilar_embedding
    )
    
    # Search with query similar to first embedding
    query_embedding = [1.0, 0.0] + [0.0] * 382
    results = await vector_store.search_similar(
        query_embedding=query_embedding,
        top_k=10,
        threshold=0.0
    )
    
    # Verify results are ordered by relevance
    assert len(results) == 3
    assert results[0].file_path == "similar.py"
    assert results[0].relevance_score > results[1].relevance_score
    assert results[1].relevance_score > results[2].relevance_score


@pytest.mark.asyncio
async def test_search_similar_respects_threshold(session):
    """Test that search_similar filters by threshold."""
    vector_store = VectorStoreService(session)
    
    # Create embeddings
    high_similarity = [1.0, 0.0] + [0.0] * 382
    await vector_store.upsert_embedding(
        file_path="high.py",
        content="High similarity",
        embedding=high_similarity
    )
    
    low_similarity = [0.0, 1.0] + [0.0] * 382
    await vector_store.upsert_embedding(
        file_path="low.py",
        content="Low similarity",
        embedding=low_similarity
    )
    
    # Search with high threshold
    query_embedding = [1.0, 0.0] + [0.0] * 382
    results = await vector_store.search_similar(
        query_embedding=query_embedding,
        top_k=10,
        threshold=0.9  # High threshold
    )
    
    # Only high similarity result should be returned
    assert len(results) == 1
    assert results[0].file_path == "high.py"


@pytest.mark.asyncio
async def test_search_similar_respects_top_k(session):
    """Test that search_similar limits results to top_k."""
    vector_store = VectorStoreService(session)
    
    # Create 5 embeddings
    for i in range(5):
        embedding = [1.0 - i * 0.1, 0.0] + [0.0] * 382
        await vector_store.upsert_embedding(
            file_path=f"file{i}.py",
            content=f"Content {i}",
            embedding=embedding
        )
    
    # Search with top_k=3
    query_embedding = [1.0, 0.0] + [0.0] * 382
    results = await vector_store.search_similar(
        query_embedding=query_embedding,
        top_k=3,
        threshold=0.0
    )
    
    # Only 3 results should be returned
    assert len(results) == 3


@pytest.mark.asyncio
async def test_search_similar_returns_impacted_file_objects(session):
    """Test that search_similar returns properly formatted ImpactedFile objects."""
    vector_store = VectorStoreService(session)
    
    # Create test embedding
    test_embedding = [1.0] + [0.0] * 383
    test_content = "x" * 300  # Content longer than 200 chars
    
    await vector_store.upsert_embedding(
        file_path="test.py",
        content=test_content,
        embedding=test_embedding
    )
    
    # Search
    results = await vector_store.search_similar(
        query_embedding=test_embedding,
        top_k=1,
        threshold=0.0
    )
    
    # Verify ImpactedFile structure
    assert len(results) == 1
    result = results[0]
    assert isinstance(result, ImpactedFile)
    assert result.file_path == "test.py"
    assert 0.0 <= result.relevance_score <= 1.0
    assert len(result.snippet) == 200  # Should be truncated to 200 chars
    assert result.snippet == test_content[:200]


@pytest.mark.asyncio
async def test_get_embedding_count(session):
    """Test that get_embedding_count returns correct count."""
    vector_store = VectorStoreService(session)
    
    # Initially should be 0
    count = await vector_store.get_embedding_count()
    assert count == 0
    
    # Add embeddings
    for i in range(3):
        await vector_store.upsert_embedding(
            file_path=f"file{i}.py",
            content=f"Content {i}",
            embedding=[0.0] * 384
        )
    
    # Should be 3
    count = await vector_store.get_embedding_count()
    assert count == 3
