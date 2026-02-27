"""
Unit tests for Sentinel Agent

Tests change detection and risk assessment functionality.
"""

import pytest
from unittest.mock import Mock, patch
from backend.agents.sentinel import sentinel_agent, _detect_changes, _assess_risk
from backend.models.state import GlobalState


class TestSentinelAgent:
    """Test suite for Sentinel Agent."""
    
    def test_sentinel_agent_with_changes_high_risk(self):
        """Test Sentinel Agent detects changes and assesses high risk."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text="Nova regra obrigatória com prazo imediato para compliance do Pix. Penalidades aplicáveis.",
            execution_id="test-123"
        )
        
        # Mock LLM to return predictable responses
        mock_llm = Mock()
        mock_llm.generate.side_effect = ["SIM", "ALTO"]
        
        with patch('backend.agents.sentinel.get_llm', return_value=mock_llm):
            # Act
            result = sentinel_agent(state)
        
        # Assert
        assert result.change_detected is True
        assert result.risk_level == "high"
        assert result.error is None
    
    def test_sentinel_agent_no_changes_low_risk(self):
        """Test Sentinel Agent detects no changes and assesses low risk."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text="Informativo sobre o sistema Pix. Apenas para conhecimento.",
            execution_id="test-456"
        )
        
        # Mock LLM
        mock_llm = Mock()
        mock_llm.generate.return_value = "NÃO"
        
        with patch('backend.agents.sentinel.get_llm', return_value=mock_llm):
            # Act
            result = sentinel_agent(state)
        
        # Assert
        assert result.change_detected is False
        assert result.risk_level == "low"
        assert result.error is None
    
    def test_sentinel_agent_with_changes_medium_risk(self):
        """Test Sentinel Agent detects changes and assesses medium risk."""
        # Arrange
        state = GlobalState(
            raw_regulatory_text="Alteração recomendada no sistema Pix com prazo moderado para implementação.",
            execution_id="test-789"
        )
        
        # Mock LLM
        mock_llm = Mock()
        mock_llm.generate.side_effect = ["SIM", "MÉDIO"]
        
        with patch('backend.agents.sentinel.get_llm', return_value=mock_llm):
            # Act
            result = sentinel_agent(state)
        
        # Assert
        assert result.change_detected is True
        assert result.risk_level == "medium"
        assert result.error is None
    
    def test_sentinel_agent_handles_llm_failure(self):
        """Test Sentinel Agent handles LLM failures gracefully when keywords present."""
        # Arrange - text with change keywords so fallback works
        state = GlobalState(
            raw_regulatory_text="Nova regra para o sistema",
            execution_id="test-error"
        )
        
        # Mock LLM to raise exception
        mock_llm = Mock()
        mock_llm.generate.side_effect = Exception("LLM connection failed")
        
        with patch('backend.agents.sentinel.get_llm', return_value=mock_llm):
            # Act
            result = sentinel_agent(state)
        
        # Assert - should use fallback logic
        assert result.change_detected is True  # "nova regra" keywords present
        assert result.risk_level in ["low", "medium"]  # fallback risk assessment
        assert result.error is None  # no error because fallback worked
    
    def test_sentinel_agent_raises_on_critical_llm_failure(self):
        """Test Sentinel Agent raises exception when LLM fails and no keywords."""
        # Arrange - text without keywords
        state = GlobalState(
            raw_regulatory_text="Test text without keywords",
            execution_id="test-critical-error"
        )
        
        # Mock LLM to raise exception
        mock_llm = Mock()
        mock_llm.generate.side_effect = Exception("LLM connection failed")
        
        with patch('backend.agents.sentinel.get_llm', return_value=mock_llm):
            # Act & Assert
            with pytest.raises(Exception):
                sentinel_agent(state)
            
            # Verify error state was set
            assert state.change_detected is False
            assert state.risk_level == "low"
            assert "Sentinel Agent error" in state.error
    
    def test_detect_changes_with_keywords(self):
        """Test change detection using keywords."""
        # Arrange
        text = "Nova regra obrigatória para alteração do sistema Pix"
        mock_llm = Mock()
        
        # Act
        result = _detect_changes(text, mock_llm)
        
        # Assert
        assert result is True
        # LLM should not be called when keywords are sufficient
        mock_llm.generate.assert_not_called()
    
    def test_detect_changes_without_keywords_uses_llm(self):
        """Test change detection falls back to LLM when keywords insufficient."""
        # Arrange
        text = "O sistema Pix precisa ser atualizado"
        mock_llm = Mock()
        mock_llm.generate.return_value = "SIM"
        
        # Act
        result = _detect_changes(text, mock_llm)
        
        # Assert
        assert result is True
        mock_llm.generate.assert_called_once()
    
    def test_assess_risk_no_changes_returns_low(self):
        """Test risk assessment returns low when no changes detected."""
        # Arrange
        text = "Informativo"
        mock_llm = Mock()
        
        # Act
        result = _assess_risk(text, mock_llm, change_detected=False)
        
        # Assert
        assert result == "low"
        mock_llm.generate.assert_not_called()
    
    def test_assess_risk_high_urgency_keywords(self):
        """Test risk assessment detects high risk from keywords."""
        # Arrange
        text = "Mudança obrigatória imediata com penalidade e multa"
        mock_llm = Mock()
        
        # Act
        result = _assess_risk(text, mock_llm, change_detected=True)
        
        # Assert
        assert result == "high"
    
    def test_assess_risk_medium_urgency_keywords(self):
        """Test risk assessment detects medium risk from keywords."""
        # Arrange
        text = "Mudança recomendada com prazo moderado"
        mock_llm = Mock()
        
        # Act
        result = _assess_risk(text, mock_llm, change_detected=True)
        
        # Assert
        assert result == "medium"
    
    def test_assess_risk_uses_llm_fallback(self):
        """Test risk assessment uses LLM when keywords insufficient."""
        # Arrange
        text = "Mudança necessária no sistema"
        mock_llm = Mock()
        mock_llm.generate.return_value = "ALTO"
        
        # Act
        result = _assess_risk(text, mock_llm, change_detected=True)
        
        # Assert
        assert result == "high"
        mock_llm.generate.assert_called_once()
    
    def test_sentinel_agent_preserves_execution_id(self):
        """Test Sentinel Agent preserves execution_id from input state."""
        # Arrange
        execution_id = "unique-execution-123"
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id=execution_id
        )
        
        mock_llm = Mock()
        mock_llm.generate.side_effect = ["NÃO", "BAIXO"]
        
        with patch('backend.agents.sentinel.get_llm', return_value=mock_llm):
            # Act
            result = sentinel_agent(state)
        
        # Assert
        assert result.execution_id == execution_id
