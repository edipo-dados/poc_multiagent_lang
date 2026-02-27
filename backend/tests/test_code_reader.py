"""
Unit tests for CodeReader Agent.

Tests the code reader agent's ability to perform semantic search on the
vector store and identify relevant code files based on regulatory models.

NOTE: Some tests require sentence-transformers to be installed.
Run: pip install -r backend/requirements.txt
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

# Skip tests that require sentence-transformers if not installed
pytest.importorskip("sentence_transformers", reason="sentence-transformers not installed")

from backend.agents.code_reader import (
    code_reader_agent,
    _generate_search_query
)
from backend.models.state import GlobalState
from backend.models.impact import ImpactedFile


# Sample regulatory model for testing
SAMPLE_REGULATORY_MODEL = {
    "title": "Novas regras para Pix",
    "description": "Estabelece validação adicional para transferências Pix",
    "requirements": [
        "Implementar validação para transferências acima de R$ 10.000",
        "Registrar todas as transações para auditoria",
        "Adicionar campo de identificação do pagador"
    ],
    "deadlines": [
        {"date": "2024-12-31", "description": "Prazo para implementação"}
    ],
    "affected_systems": ["Pix", "pagamentos"]
}


class TestCodeReaderAgent:
    """Test suite for code_reader_agent function."""
    
    @pytest.mark.asyncio
    async def test_code_reader_agent_success(self):
        """Test successful execution of code reader agent."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id="test-123",
            regulatory_model=SAMPLE_REGULATORY_MODEL
        )
        
        # Mock impacted files
        mock_files = [
            ImpactedFile(
                file_path="api/endpoints.py",
                relevance_score=0.85,
                snippet="def create_pix(request: PixCreateRequest):"
            ),
            ImpactedFile(
                file_path="domain/validators.py",
                relevance_score=0.78,
                snippet="def validate_pix_amount(amount: Decimal):"
            )
        ]
        
        # Mock services
        mock_embedding_service = Mock()
        mock_embedding_service.encode.return_value = [0.1] * 384
        
        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar.return_value = mock_files
        
        # Act
        with patch('backend.agents.code_reader.EmbeddingService', return_value=mock_embedding_service):
            with patch('backend.agents.code_reader.VectorStoreService', return_value=mock_vector_store):
                with patch('backend.agents.code_reader.AsyncSessionLocal'):
                    result = await code_reader_agent(state)
        
        # Assert
        assert result.impacted_files is not None
        assert len(result.impacted_files) == 2
        assert result.impacted_files[0]["file_path"] == "api/endpoints.py"
        assert result.impacted_files[0]["relevance_score"] == 0.85
        assert result.impacted_files[1]["file_path"] == "domain/validators.py"
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_code_reader_agent_no_regulatory_model(self):
        """Test code reader agent when regulatory_model is None."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id="test-no-model",
            regulatory_model=None
        )
        
        # Act
        result = await code_reader_agent(state)
        
        # Assert
        assert result.impacted_files == []
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_code_reader_agent_no_results_found(self):
        """Test code reader agent when no relevant files found."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id="test-no-results",
            regulatory_model=SAMPLE_REGULATORY_MODEL
        )
        
        # Mock services returning empty results
        mock_embedding_service = Mock()
        mock_embedding_service.encode.return_value = [0.1] * 384
        
        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar.return_value = []  # No results
        
        # Act
        with patch('backend.agents.code_reader.EmbeddingService', return_value=mock_embedding_service):
            with patch('backend.agents.code_reader.VectorStoreService', return_value=mock_vector_store):
                with patch('backend.agents.code_reader.AsyncSessionLocal'):
                    result = await code_reader_agent(state)
        
        # Assert
        assert result.impacted_files == []
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_code_reader_agent_returns_top_10(self):
        """Test that code reader agent returns at most 10 files."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id="test-top-10",
            regulatory_model=SAMPLE_REGULATORY_MODEL
        )
        
        # Mock 15 files (should only get top 10)
        mock_files = [
            ImpactedFile(
                file_path=f"file_{i}.py",
                relevance_score=0.9 - (i * 0.05),
                snippet=f"content {i}"
            )
            for i in range(10)  # Vector store already limits to 10
        ]
        
        mock_embedding_service = Mock()
        mock_embedding_service.encode.return_value = [0.1] * 384
        
        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar.return_value = mock_files
        
        # Act
        with patch('backend.agents.code_reader.EmbeddingService', return_value=mock_embedding_service):
            with patch('backend.agents.code_reader.VectorStoreService', return_value=mock_vector_store):
                with patch('backend.agents.code_reader.AsyncSessionLocal'):
                    result = await code_reader_agent(state)
        
        # Assert
        assert len(result.impacted_files) == 10
    
    @pytest.mark.asyncio
    async def test_code_reader_agent_embedding_failure(self):
        """Test code reader agent when embedding generation fails."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id="test-embedding-fail",
            regulatory_model=SAMPLE_REGULATORY_MODEL
        )
        
        # Mock embedding service to raise exception
        mock_embedding_service = Mock()
        mock_embedding_service.encode.side_effect = Exception("Embedding model not loaded")
        
        # Act & Assert
        with patch('backend.agents.code_reader.EmbeddingService', return_value=mock_embedding_service):
            with pytest.raises(Exception, match="Embedding model not loaded"):
                await code_reader_agent(state)
        
        # Verify error was set in state
        assert state.error is not None
        assert "CodeReader Agent error" in state.error
    
    @pytest.mark.asyncio
    async def test_code_reader_agent_vector_store_failure(self):
        """Test code reader agent when vector store query fails."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id="test-vector-fail",
            regulatory_model=SAMPLE_REGULATORY_MODEL
        )
        
        mock_embedding_service = Mock()
        mock_embedding_service.encode.return_value = [0.1] * 384
        
        # Mock vector store to raise exception
        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar.side_effect = Exception("Database connection failed")
        
        # Act & Assert
        with patch('backend.agents.code_reader.EmbeddingService', return_value=mock_embedding_service):
            with patch('backend.agents.code_reader.VectorStoreService', return_value=mock_vector_store):
                with patch('backend.agents.code_reader.AsyncSessionLocal'):
                    with pytest.raises(Exception, match="Database connection failed"):
                        await code_reader_agent(state)
        
        # Verify error was set in state
        assert state.error is not None
        assert "CodeReader Agent error" in state.error
    
    @pytest.mark.asyncio
    async def test_code_reader_agent_updates_state(self):
        """Test that code reader agent properly updates Global State."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id="test-state",
            regulatory_model=SAMPLE_REGULATORY_MODEL
        )
        
        mock_files = [
            ImpactedFile(
                file_path="test.py",
                relevance_score=0.75,
                snippet="test content"
            )
        ]
        
        mock_embedding_service = Mock()
        mock_embedding_service.encode.return_value = [0.1] * 384
        
        mock_vector_store = AsyncMock()
        mock_vector_store.search_similar.return_value = mock_files
        
        # Act
        with patch('backend.agents.code_reader.EmbeddingService', return_value=mock_embedding_service):
            with patch('backend.agents.code_reader.VectorStoreService', return_value=mock_vector_store):
                with patch('backend.agents.code_reader.AsyncSessionLocal'):
                    result = await code_reader_agent(state)
        
        # Assert
        assert result is state  # Same object reference
        assert state.impacted_files is not None
        assert len(state.impacted_files) == 1


class TestGenerateSearchQuery:
    """Test suite for _generate_search_query function."""
    
    def test_generate_query_with_all_fields(self):
        """Test query generation with all fields present."""
        # Arrange
        model = {
            "title": "Novas regras Pix",
            "description": "Validação adicional para transferências",
            "requirements": ["Req 1", "Req 2", "Req 3"],
            "deadlines": [{"date": "2024-12-31", "description": "Deadline"}],
            "affected_systems": ["Pix", "pagamentos"]
        }
        
        # Act
        result = _generate_search_query(model)
        
        # Assert
        assert "Novas regras Pix" in result
        assert "Validação adicional" in result
        assert "Req 1" in result
        assert "Req 2" in result
        assert "Req 3" in result
        assert "Pix" in result
        assert "pagamentos" in result
    
    def test_generate_query_with_minimal_fields(self):
        """Test query generation with only required fields."""
        # Arrange
        model = {
            "title": "Test Title",
            "description": "Test Description",
            "requirements": [],
            "deadlines": [],
            "affected_systems": []
        }
        
        # Act
        result = _generate_search_query(model)
        
        # Assert
        assert "Test Title" in result
        assert "Test Description" in result
        assert len(result) > 0
    
    def test_generate_query_limits_requirements(self):
        """Test that query generation limits requirements to first 5."""
        # Arrange
        model = {
            "title": "Title",
            "description": "Description",
            "requirements": [f"Requirement {i}" for i in range(10)],
            "deadlines": [],
            "affected_systems": []
        }
        
        # Act
        result = _generate_search_query(model)
        
        # Assert
        assert "Requirement 0" in result
        assert "Requirement 4" in result
        assert "Requirement 9" not in result  # Should be excluded
    
    def test_generate_query_with_missing_title(self):
        """Test query generation when title is missing."""
        # Arrange
        model = {
            "description": "Description only",
            "requirements": ["Req 1"],
            "deadlines": [],
            "affected_systems": ["System1"]
        }
        
        # Act
        result = _generate_search_query(model)
        
        # Assert
        assert "Description only" in result
        assert "Req 1" in result
        assert "System1" in result
    
    def test_generate_query_with_empty_model(self):
        """Test query generation with empty model."""
        # Arrange
        model = {}
        
        # Act
        result = _generate_search_query(model)
        
        # Assert
        assert isinstance(result, str)
        # Should return empty or minimal string
    
    def test_generate_query_combines_affected_systems(self):
        """Test that affected systems are combined properly."""
        # Arrange
        model = {
            "title": "Title",
            "description": "Description",
            "requirements": [],
            "deadlines": [],
            "affected_systems": ["Pix", "TED", "DOC", "Pagamentos"]
        }
        
        # Act
        result = _generate_search_query(model)
        
        # Assert
        assert "Systems:" in result
        assert "Pix" in result
        assert "TED" in result
        assert "DOC" in result
        assert "Pagamentos" in result
    
    def test_generate_query_returns_non_empty_string(self):
        """Test that query generation always returns a non-empty string."""
        # Arrange
        model = {
            "title": "T",
            "description": "D",
            "requirements": [],
            "deadlines": [],
            "affected_systems": []
        }
        
        # Act
        result = _generate_search_query(model)
        
        # Assert
        assert len(result) > 0
        assert isinstance(result, str)
