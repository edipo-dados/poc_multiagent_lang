"""
Unit tests for Translator Agent.

Tests the translator agent's ability to extract structured information
from regulatory text and create valid RegulatoryModel objects.
"""

import pytest
import json
from unittest.mock import Mock, patch
from backend.agents.translator import (
    translator_agent,
    _extract_structured_data,
    _extract_json_from_response,
    _validate_regulatory_model,
    _test_round_trip_serialization,
    _create_fallback_model
)
from backend.models.state import GlobalState
from backend.models.regulatory import RegulatoryModel


# Sample regulatory text for testing
SAMPLE_REGULATORY_TEXT = """
Resolução BCB nº 123/2024

O Banco Central do Brasil estabelece novas regras para o sistema Pix.

Artigo 1º: As instituições financeiras devem implementar validação adicional
para transferências Pix acima de R$ 10.000,00.

Artigo 2º: O prazo para implementação é 31 de dezembro de 2024.

Artigo 3º: O sistema de pagamentos instantâneos deve registrar todas as
transações para fins de auditoria.
"""


class TestTranslatorAgent:
    """Test suite for translator_agent function."""
    
    def test_translator_agent_success(self):
        """Test successful execution of translator agent."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text=SAMPLE_REGULATORY_TEXT,
            execution_id="test-123"
        )
        
        mock_llm = Mock()
        mock_llm.generate.return_value = json.dumps({
            "title": "Novas regras para Pix",
            "description": "Estabelece validação adicional para transferências",
            "requirements": [
                "Implementar validação para transferências acima de R$ 10.000",
                "Registrar todas as transações"
            ],
            "deadlines": [
                {"date": "2024-12-31", "description": "Prazo para implementação"}
            ],
            "affected_systems": ["Pix", "pagamentos"]
        })
        
        # Act
        with patch('backend.agents.translator.get_llm', return_value=mock_llm):
            result = translator_agent(state)
        
        # Assert
        assert result.regulatory_model is not None
        assert result.regulatory_model["title"] == "Novas regras para Pix"
        assert len(result.regulatory_model["requirements"]) == 2
        assert len(result.regulatory_model["deadlines"]) == 1
        assert "Pix" in result.regulatory_model["affected_systems"]
        assert result.error is None
    
    def test_translator_agent_with_empty_text(self):
        """Test translator agent with empty regulatory text uses fallback."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text="",
            execution_id="test-empty"
        )
        
        mock_llm = Mock()
        mock_llm.generate.side_effect = Exception("Empty text")
        
        # Act
        with patch('backend.agents.translator.get_llm', return_value=mock_llm):
            result = translator_agent(state)
        
        # Assert - should use fallback model
        assert result.regulatory_model is not None
        assert result.regulatory_model["title"] == "Regulatory Change"
        assert "Manual review required" in result.regulatory_model["requirements"][0]
    
    def test_translator_agent_llm_failure_uses_fallback(self):
        """Test that agent uses fallback model when LLM fails."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text=SAMPLE_REGULATORY_TEXT,
            execution_id="test-fallback"
        )
        
        mock_llm = Mock()
        mock_llm.generate.side_effect = Exception("LLM unavailable")
        
        # Act
        with patch('backend.agents.translator.get_llm', return_value=mock_llm):
            result = translator_agent(state)
        
        # Assert
        assert result.regulatory_model is not None
        assert result.regulatory_model["title"] is not None
        assert "Manual review required" in result.regulatory_model["requirements"][0]
    
    def test_translator_agent_updates_state(self):
        """Test that translator agent properly updates Global State."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text=SAMPLE_REGULATORY_TEXT,
            execution_id="test-state"
        )
        
        mock_llm = Mock()
        mock_llm.generate.return_value = json.dumps({
            "title": "Test Title",
            "description": "Test Description",
            "requirements": ["Req 1"],
            "deadlines": [],
            "affected_systems": ["Pix"]
        })
        
        # Act
        with patch('backend.agents.translator.get_llm', return_value=mock_llm):
            result = translator_agent(state)
        
        # Assert
        assert result is state  # Same object reference
        assert state.regulatory_model is not None


class TestExtractStructuredData:
    """Test suite for _extract_structured_data function."""
    
    def test_extract_with_valid_json_response(self):
        """Test extraction with clean JSON response from LLM."""
        # Arrange
        mock_llm = Mock()
        mock_llm.generate.return_value = json.dumps({
            "title": "Test Regulation",
            "description": "Test description",
            "requirements": ["Requirement 1", "Requirement 2"],
            "deadlines": [{"date": "2024-12-31", "description": "Implementation"}],
            "affected_systems": ["Pix"]
        })
        
        # Act
        result = _extract_structured_data(SAMPLE_REGULATORY_TEXT, mock_llm)
        
        # Assert
        assert isinstance(result, RegulatoryModel)
        assert result.title == "Test Regulation"
        assert len(result.requirements) == 2
        assert len(result.deadlines) == 1
    
    def test_extract_with_json_wrapped_in_text(self):
        """Test extraction when JSON is wrapped in extra text."""
        # Arrange
        mock_llm = Mock()
        mock_llm.generate.return_value = """
        Here is the extracted information:
        {
            "title": "Wrapped JSON",
            "description": "Description",
            "requirements": [],
            "deadlines": [],
            "affected_systems": []
        }
        That's all!
        """
        
        # Act
        result = _extract_structured_data(SAMPLE_REGULATORY_TEXT, mock_llm)
        
        # Assert
        assert isinstance(result, RegulatoryModel)
        assert result.title == "Wrapped JSON"
    
    def test_extract_with_llm_failure_returns_fallback(self):
        """Test that fallback model is returned when LLM fails."""
        # Arrange
        mock_llm = Mock()
        mock_llm.generate.side_effect = Exception("LLM error")
        
        # Act
        result = _extract_structured_data(SAMPLE_REGULATORY_TEXT, mock_llm)
        
        # Assert
        assert isinstance(result, RegulatoryModel)
        assert "Manual review required" in result.requirements[0]


class TestExtractJsonFromResponse:
    """Test suite for _extract_json_from_response function."""
    
    def test_extract_clean_json(self):
        """Test extraction of clean JSON."""
        # Arrange
        response = '{"key": "value", "number": 123}'
        
        # Act
        result = _extract_json_from_response(response)
        
        # Assert
        assert result == {"key": "value", "number": 123}
    
    def test_extract_json_with_whitespace(self):
        """Test extraction with leading/trailing whitespace."""
        # Arrange
        response = '  \n  {"key": "value"}  \n  '
        
        # Act
        result = _extract_json_from_response(response)
        
        # Assert
        assert result == {"key": "value"}
    
    def test_extract_json_from_text(self):
        """Test extraction when JSON is embedded in text."""
        # Arrange
        response = 'Here is the data: {"key": "value"} end of data'
        
        # Act
        result = _extract_json_from_response(response)
        
        # Assert
        assert result == {"key": "value"}
    
    def test_extract_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError."""
        # Arrange
        response = "This is not JSON at all"
        
        # Act & Assert
        with pytest.raises(ValueError, match="No valid JSON object found"):
            _extract_json_from_response(response)


class TestValidateRegulatoryModel:
    """Test suite for _validate_regulatory_model function."""
    
    def test_validate_valid_model(self):
        """Test validation of a valid model."""
        # Arrange
        model = RegulatoryModel(
            title="Valid Title",
            description="Valid description",
            requirements=["Req 1"],
            deadlines=[{"date": "2024-12-31", "description": "Deadline"}],
            affected_systems=["Pix"]
        )
        
        # Act & Assert (should not raise)
        _validate_regulatory_model(model)
    
    def test_validate_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        # Arrange
        model = RegulatoryModel(
            title="",
            description="Description",
            requirements=[],
            deadlines=[],
            affected_systems=[]
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="non-empty title"):
            _validate_regulatory_model(model)
    
    def test_validate_empty_description_raises_error(self):
        """Test that empty description raises ValueError."""
        # Arrange
        model = RegulatoryModel(
            title="Title",
            description="   ",
            requirements=[],
            deadlines=[],
            affected_systems=[]
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="non-empty description"):
            _validate_regulatory_model(model)
    
    def test_validate_invalid_deadline_structure(self):
        """Test that invalid deadline structure raises ValueError."""
        # Arrange
        model = RegulatoryModel(
            title="Title",
            description="Description",
            requirements=[],
            deadlines=[{"date": "2024-12-31"}],  # Missing 'description'
            affected_systems=[]
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="'date' and 'description'"):
            _validate_regulatory_model(model)


class TestRoundTripSerialization:
    """Test suite for _test_round_trip_serialization function."""
    
    def test_round_trip_success(self):
        """Test successful round-trip serialization."""
        # Arrange
        model = RegulatoryModel(
            title="Test",
            description="Description",
            requirements=["Req 1", "Req 2"],
            deadlines=[{"date": "2024-12-31", "description": "Deadline"}],
            affected_systems=["Pix", "Pagamentos"]
        )
        
        # Act & Assert (should not raise)
        _test_round_trip_serialization(model)
    
    def test_round_trip_with_empty_lists(self):
        """Test round-trip with empty lists."""
        # Arrange
        model = RegulatoryModel(
            title="Test",
            description="Description",
            requirements=[],
            deadlines=[],
            affected_systems=[]
        )
        
        # Act & Assert (should not raise)
        _test_round_trip_serialization(model)


class TestCreateFallbackModel:
    """Test suite for _create_fallback_model function."""
    
    def test_fallback_with_normal_text(self):
        """Test fallback model creation with normal text."""
        # Arrange
        text = "Resolução BCB sobre Pix\nArtigo 1: Novas regras..."
        
        # Act
        result = _create_fallback_model(text)
        
        # Assert
        assert isinstance(result, RegulatoryModel)
        assert result.title == "Resolução BCB sobre Pix"
        assert "Manual review required" in result.requirements[0]
        assert "Pix" in result.affected_systems
    
    def test_fallback_with_empty_text(self):
        """Test fallback model creation with empty text."""
        # Arrange
        text = ""
        
        # Act
        result = _create_fallback_model(text)
        
        # Assert
        assert isinstance(result, RegulatoryModel)
        assert result.title == "Regulatory Change"
        assert result.description == "No description available"
    
    def test_fallback_identifies_system_keywords(self):
        """Test that fallback identifies system keywords."""
        # Arrange
        text = "Nova regra para transferências e pagamentos via TED"
        
        # Act
        result = _create_fallback_model(text)
        
        # Assert
        assert "Transferência" in result.affected_systems or "Ted" in result.affected_systems
    
    def test_fallback_with_long_text(self):
        """Test fallback with text longer than 100 chars."""
        # Arrange
        text = "A" * 200
        
        # Act
        result = _create_fallback_model(text)
        
        # Assert
        assert len(result.title) <= 100
        assert len(result.description) <= 500
