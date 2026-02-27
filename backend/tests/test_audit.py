"""
Unit tests for Audit Service.

Tests save_execution and retrieve_execution methods with various
Global State configurations.
"""

import pytest
import pytest_asyncio
from datetime import datetime, UTC
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from backend.database.models import Base, AuditLog
from backend.services.audit import AuditService
from backend.models.state import GlobalState


# Test database URL (use test database)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/regulatory_ai_test"


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine."""
    from sqlalchemy import text
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )
    
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


@pytest_asyncio.fixture
async def test_session(test_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def sample_state():
    """Create sample Global State for testing."""
    return GlobalState(
        raw_regulatory_text="Sample regulatory text for testing",
        change_detected=True,
        risk_level="high",
        regulatory_model={
            "title": "Test Regulation",
            "description": "Test description",
            "requirements": ["Requirement 1", "Requirement 2"],
            "deadlines": [{"date": "2024-12-31", "description": "Implementation deadline"}],
            "affected_systems": ["Pix"]
        },
        impacted_files=[
            {
                "file_path": "api/endpoints.py",
                "relevance_score": 0.85,
                "snippet": "Sample code snippet"
            }
        ],
        impact_analysis=[
            {
                "file_path": "api/endpoints.py",
                "impact_type": "business_logic",
                "severity": "high",
                "description": "Test impact",
                "suggested_changes": ["Change 1", "Change 2"]
            }
        ],
        technical_spec="# Technical Specification\n\nTest spec content",
        kiro_prompt="CONTEXT:\nTest context",
        execution_timestamp=datetime.now(UTC),
        execution_id=str(uuid4()),
        error=None
    )


@pytest.mark.asyncio
async def test_save_execution_creates_audit_log(test_session, sample_state):
    """Test that save_execution creates an audit log entry."""
    audit_service = AuditService(test_session)
    
    # Save execution
    execution_id = await audit_service.save_execution(sample_state)
    
    # Verify execution_id returned
    assert execution_id == sample_state.execution_id
    
    # Verify audit log was created in database
    from sqlalchemy import select
    stmt = select(AuditLog).where(AuditLog.execution_id == execution_id)
    result = await test_session.execute(stmt)
    audit_entry = result.scalar_one_or_none()
    
    assert audit_entry is not None
    assert audit_entry.execution_id == sample_state.execution_id
    assert audit_entry.raw_text == sample_state.raw_regulatory_text
    assert audit_entry.change_detected == sample_state.change_detected
    assert audit_entry.risk_level == sample_state.risk_level


@pytest.mark.asyncio
async def test_save_execution_stores_all_fields(test_session, sample_state):
    """Test that save_execution stores all Global State fields."""
    audit_service = AuditService(test_session)
    
    # Save execution
    await audit_service.save_execution(sample_state)
    
    # Retrieve from database
    from sqlalchemy import select
    stmt = select(AuditLog).where(AuditLog.execution_id == sample_state.execution_id)
    result = await test_session.execute(stmt)
    audit_entry = result.scalar_one()
    
    # Verify all fields
    assert audit_entry.raw_text == sample_state.raw_regulatory_text
    assert audit_entry.change_detected == sample_state.change_detected
    assert audit_entry.risk_level == sample_state.risk_level
    assert audit_entry.structured_model == sample_state.regulatory_model
    assert audit_entry.impacted_files == sample_state.impacted_files
    assert audit_entry.impact_analysis == sample_state.impact_analysis
    assert audit_entry.technical_spec == sample_state.technical_spec
    assert audit_entry.kiro_prompt == sample_state.kiro_prompt
    assert audit_entry.error == sample_state.error


@pytest.mark.asyncio
async def test_retrieve_execution_returns_state(test_session, sample_state):
    """Test that retrieve_execution reconstructs Global State."""
    audit_service = AuditService(test_session)
    
    # Save execution
    execution_id = await audit_service.save_execution(sample_state)
    
    # Retrieve execution
    retrieved_state = await audit_service.retrieve_execution(execution_id)
    
    # Verify state was retrieved
    assert retrieved_state is not None
    assert retrieved_state.execution_id == sample_state.execution_id
    assert retrieved_state.raw_regulatory_text == sample_state.raw_regulatory_text
    assert retrieved_state.change_detected == sample_state.change_detected
    assert retrieved_state.risk_level == sample_state.risk_level
    assert retrieved_state.regulatory_model == sample_state.regulatory_model
    assert retrieved_state.impacted_files == sample_state.impacted_files
    assert retrieved_state.impact_analysis == sample_state.impact_analysis
    assert retrieved_state.technical_spec == sample_state.technical_spec
    assert retrieved_state.kiro_prompt == sample_state.kiro_prompt


@pytest.mark.asyncio
async def test_retrieve_execution_returns_none_for_invalid_id(test_session):
    """Test that retrieve_execution returns None for non-existent execution_id."""
    audit_service = AuditService(test_session)
    
    # Try to retrieve non-existent execution
    retrieved_state = await audit_service.retrieve_execution("invalid-uuid")
    
    # Verify None returned
    assert retrieved_state is None


@pytest.mark.asyncio
async def test_save_execution_with_error(test_session):
    """Test that save_execution handles state with error field."""
    audit_service = AuditService(test_session)
    
    # Create state with error
    error_state = GlobalState(
        raw_regulatory_text="Test text",
        execution_id=str(uuid4()),
        error="Sentinel agent failed: Connection timeout"
    )
    
    # Save execution
    execution_id = await audit_service.save_execution(error_state)
    
    # Retrieve and verify error was saved
    retrieved_state = await audit_service.retrieve_execution(execution_id)
    assert retrieved_state is not None
    assert retrieved_state.error == "Sentinel agent failed: Connection timeout"


@pytest.mark.asyncio
async def test_save_execution_with_partial_state(test_session):
    """Test that save_execution handles partial state (early failure)."""
    audit_service = AuditService(test_session)
    
    # Create partial state (only Sentinel outputs)
    partial_state = GlobalState(
        raw_regulatory_text="Test text",
        change_detected=True,
        risk_level="medium",
        execution_id=str(uuid4()),
        error="Translator agent failed"
    )
    
    # Save execution
    execution_id = await audit_service.save_execution(partial_state)
    
    # Retrieve and verify partial state
    retrieved_state = await audit_service.retrieve_execution(execution_id)
    assert retrieved_state is not None
    assert retrieved_state.change_detected == True
    assert retrieved_state.risk_level == "medium"
    assert retrieved_state.regulatory_model is None
    assert retrieved_state.impacted_files == []
    assert retrieved_state.error == "Translator agent failed"


@pytest.mark.asyncio
async def test_retrieve_execution_handles_null_lists(test_session):
    """Test that retrieve_execution handles NULL JSONB fields as empty lists."""
    audit_service = AuditService(test_session)
    
    # Create state with no impacted files or impact analysis
    minimal_state = GlobalState(
        raw_regulatory_text="Minimal test",
        execution_id=str(uuid4())
    )
    
    # Save and retrieve
    execution_id = await audit_service.save_execution(minimal_state)
    retrieved_state = await audit_service.retrieve_execution(execution_id)
    
    # Verify empty lists are returned for NULL JSONB fields
    assert retrieved_state is not None
    assert retrieved_state.impacted_files == []
    assert retrieved_state.impact_analysis == []
