"""
Integration tests for Impact Agent with real Pix repository files.

Tests the Impact Agent's ability to analyze actual files from the
fake Pix repository.
"""

import pytest
from unittest.mock import Mock, patch
from backend.agents.impact import impact_agent
from backend.models.state import GlobalState


class TestImpactAgentIntegration:
    """Integration tests with real Pix repository files."""
    
    @patch('backend.agents.impact.get_llm')
    def test_analyze_real_pix_files(self, mock_get_llm):
        """Test analyzing real files from fake Pix repository."""
        # Setup mock LLM
        mock_llm = Mock()
        mock_llm.generate.return_value = """
SEVERIDADE: HIGH
DESCRIÇÃO: O arquivo precisa ser atualizado para suportar novos campos obrigatórios do Pix.
MUDANÇAS:
- Adicionar campo de identificação única
- Implementar validação de formato
- Atualizar documentação da API
"""
        mock_get_llm.return_value = mock_llm
        
        # Create state with real file paths
        state = GlobalState(
            raw_regulatory_text="Nova regulação do Pix exige campos adicionais",
            regulatory_model={
                "title": "Atualização Regulatória Pix 2024",
                "description": "Novos campos obrigatórios para transações Pix",
                "requirements": [
                    "Adicionar campo de identificação única",
                    "Implementar validação de formato",
                    "Garantir rastreabilidade completa"
                ],
                "deadlines": [
                    {"date": "2024-12-31", "description": "Implementação obrigatória"}
                ],
                "affected_systems": ["Pix", "Pagamentos"]
            },
            impacted_files=[
                {
                    "file_path": "api/endpoints.py",
                    "relevance_score": 0.92,
                    "snippet": "FastAPI endpoints for Pix operations"
                },
                {
                    "file_path": "api/schemas.py",
                    "relevance_score": 0.88,
                    "snippet": "Pydantic schemas for API"
                },
                {
                    "file_path": "domain/validators.py",
                    "relevance_score": 0.85,
                    "snippet": "Business rule validators"
                },
                {
                    "file_path": "database/models.py",
                    "relevance_score": 0.80,
                    "snippet": "SQLAlchemy ORM models"
                }
            ],
            execution_id="integration-test-123"
        )
        
        # Run impact agent
        result = impact_agent(state)
        
        # Verify results
        assert result.error is None
        assert len(result.impact_analysis) == 4
        
        # Check each file was analyzed
        file_paths = [impact["file_path"] for impact in result.impact_analysis]
        assert "api/endpoints.py" in file_paths
        assert "api/schemas.py" in file_paths
        assert "domain/validators.py" in file_paths
        assert "database/models.py" in file_paths
        
        # Verify impact types are correctly classified
        impact_by_path = {imp["file_path"]: imp for imp in result.impact_analysis}
        
        assert impact_by_path["api/endpoints.py"]["impact_type"] == "api_contract"
        assert impact_by_path["api/schemas.py"]["impact_type"] == "api_contract"
        assert impact_by_path["domain/validators.py"]["impact_type"] == "validation"
        assert impact_by_path["database/models.py"]["impact_type"] == "schema_change"
        
        # Verify all impacts have required fields
        for impact in result.impact_analysis:
            assert "file_path" in impact
            assert "impact_type" in impact
            assert "severity" in impact
            assert "description" in impact
            assert "suggested_changes" in impact
            assert isinstance(impact["suggested_changes"], list)
            assert len(impact["suggested_changes"]) > 0
    
    @patch('backend.agents.impact.get_llm')
    def test_analyze_with_missing_file(self, mock_get_llm):
        """Test handling of missing files gracefully."""
        mock_llm = Mock()
        mock_llm.generate.return_value = "SEVERIDADE: MEDIUM\nDESCRIÇÃO: Test\nMUDANÇAS:\n- Change 1"
        mock_get_llm.return_value = mock_llm
        
        state = GlobalState(
            raw_regulatory_text="Test regulation",
            regulatory_model={
                "title": "Test",
                "description": "Test",
                "requirements": ["Req 1"],
                "deadlines": [],
                "affected_systems": ["Pix"]
            },
            impacted_files=[
                {"file_path": "nonexistent/file.py", "relevance_score": 0.9},
                {"file_path": "api/endpoints.py", "relevance_score": 0.8}
            ],
            execution_id="test-missing-file"
        )
        
        result = impact_agent(state)
        
        # Should continue and analyze the existing file
        assert result.error is None
        assert len(result.impact_analysis) == 1
        assert result.impact_analysis[0]["file_path"] == "api/endpoints.py"
    
    @patch('backend.agents.impact.get_llm')
    def test_severity_levels_are_valid(self, mock_get_llm):
        """Test that all severity levels are valid."""
        # Mock different severity responses
        responses = [
            "SEVERIDADE: HIGH\nDESCRIÇÃO: High severity\nMUDANÇAS:\n- Change 1",
            "SEVERIDADE: MEDIUM\nDESCRIÇÃO: Medium severity\nMUDANÇAS:\n- Change 2",
            "SEVERIDADE: LOW\nDESCRIÇÃO: Low severity\nMUDANÇAS:\n- Change 3"
        ]
        
        mock_llm = Mock()
        mock_llm.generate.side_effect = responses
        mock_get_llm.return_value = mock_llm
        
        state = GlobalState(
            raw_regulatory_text="Test regulation",
            regulatory_model={
                "title": "Test",
                "description": "Test",
                "requirements": ["Req 1"],
                "deadlines": [],
                "affected_systems": ["Pix"]
            },
            impacted_files=[
                {"file_path": "api/endpoints.py", "relevance_score": 0.9},
                {"file_path": "domain/validators.py", "relevance_score": 0.8},
                {"file_path": "database/models.py", "relevance_score": 0.7}
            ],
            execution_id="test-severity"
        )
        
        result = impact_agent(state)
        
        # Verify all severities are valid
        valid_severities = {"low", "medium", "high"}
        for impact in result.impact_analysis:
            assert impact["severity"] in valid_severities
    
    @patch('backend.agents.impact.get_llm')
    def test_impact_types_are_valid(self, mock_get_llm):
        """Test that all impact types are valid."""
        mock_llm = Mock()
        mock_llm.generate.return_value = "SEVERIDADE: MEDIUM\nDESCRIÇÃO: Test\nMUDANÇAS:\n- Change 1"
        mock_get_llm.return_value = mock_llm
        
        state = GlobalState(
            raw_regulatory_text="Test regulation",
            regulatory_model={
                "title": "Test",
                "description": "Test",
                "requirements": ["Req 1"],
                "deadlines": [],
                "affected_systems": ["Pix"]
            },
            impacted_files=[
                {"file_path": "api/endpoints.py", "relevance_score": 0.9},
                {"file_path": "api/schemas.py", "relevance_score": 0.85},
                {"file_path": "domain/validators.py", "relevance_score": 0.8},
                {"file_path": "database/models.py", "relevance_score": 0.75},
                {"file_path": "services/pix_service.py", "relevance_score": 0.7}
            ],
            execution_id="test-impact-types"
        )
        
        result = impact_agent(state)
        
        # Verify all impact types are valid
        valid_types = {"schema_change", "business_logic", "validation", "api_contract"}
        for impact in result.impact_analysis:
            assert impact["impact_type"] in valid_types
