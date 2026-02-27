"""
Unit tests for SpecGenerator Agent.

Tests the SpecGenerator Agent's ability to generate technical specifications
from regulatory models and impact analysis.
"""

import pytest
from unittest.mock import Mock, patch
from backend.agents.spec_generator import (
    spec_generator_agent,
    _generate_technical_spec,
    _generate_overview,
    _generate_affected_components,
    _generate_required_changes,
    _generate_acceptance_criteria,
    _calculate_estimated_effort,
    _generate_minimal_spec
)
from backend.models.state import GlobalState


class TestSpecGeneratorAgent:
    """Test suite for the main spec_generator_agent function."""
    
    def test_spec_generator_agent_without_regulatory_model(self):
        """Test that agent raises error when regulatory_model is missing."""
        state = GlobalState(
            raw_regulatory_text="Test regulation",
            impact_analysis=[],
            execution_id="test-123"
        )
        
        with pytest.raises(ValueError, match="regulatory_model is required"):
            spec_generator_agent(state)
    
    def test_spec_generator_agent_with_no_impact_analysis(self):
        """Test that agent generates minimal spec when no impact analysis."""
        state = GlobalState(
            raw_regulatory_text="Test regulation",
            regulatory_model={
                "title": "Test Regulation",
                "description": "Test description",
                "requirements": ["Req 1"],
                "deadlines": [],
                "affected_systems": ["Pix"]
            },
            impact_analysis=[],
            execution_id="test-123"
        )
        
        result = spec_generator_agent(state)
        
        assert result.technical_spec is not None
        assert "Test Regulation" in result.technical_spec
        assert "No impacted components identified" in result.technical_spec
        assert result.error is None
    
    @patch('backend.agents.spec_generator.get_llm')
    def test_spec_generator_agent_generates_complete_spec(self, mock_get_llm):
        """Test that agent generates complete specification."""
        # Setup mock LLM
        mock_llm = Mock()
        mock_llm.generate.return_value = "Test overview content"
        mock_get_llm.return_value = mock_llm
        
        state = GlobalState(
            raw_regulatory_text="Test regulation",
            regulatory_model={
                "title": "New Pix Requirements",
                "description": "Updated Pix validation rules",
                "requirements": ["Add field validation", "Update API schema"],
                "deadlines": [{"date": "2024-12-31", "description": "Implementation deadline"}],
                "affected_systems": ["Pix"]
            },
            impact_analysis=[
                {
                    "file_path": "api/endpoints.py",
                    "impact_type": "api_contract",
                    "severity": "high",
                    "description": "API changes needed",
                    "suggested_changes": ["Update endpoint", "Add validation"]
                },
                {
                    "file_path": "domain/validators.py",
                    "impact_type": "validation",
                    "severity": "medium",
                    "description": "Validation updates needed",
                    "suggested_changes": ["Add new validator"]
                }
            ],
            execution_id="test-123"
        )
        
        result = spec_generator_agent(state)
        
        assert result.technical_spec is not None
        assert "New Pix Requirements" in result.technical_spec
        assert "## Overview" in result.technical_spec
        assert "## Affected Components" in result.technical_spec
        assert "## Required Changes" in result.technical_spec
        assert "## Acceptance Criteria" in result.technical_spec
        assert "## Estimated Effort" in result.technical_spec
        assert "api/endpoints.py" in result.technical_spec
        assert "domain/validators.py" in result.technical_spec
        assert result.error is None


class TestGenerateAffectedComponents:
    """Test suite for _generate_affected_components function."""
    
    def test_generate_affected_components_groups_by_type(self):
        """Test that components are grouped by impact type."""
        impact_analysis = [
            {
                "file_path": "api/endpoints.py",
                "impact_type": "api_contract",
                "severity": "high"
            },
            {
                "file_path": "api/schemas.py",
                "impact_type": "api_contract",
                "severity": "medium"
            },
            {
                "file_path": "domain/validators.py",
                "impact_type": "validation",
                "severity": "low"
            }
        ]
        
        result = _generate_affected_components(impact_analysis)
        
        assert "API Contracts" in result
        assert "Validation Rules" in result
        assert "api/endpoints.py" in result
        assert "api/schemas.py" in result
        assert "domain/validators.py" in result
        assert "HIGH" in result
        assert "MEDIUM" in result
        assert "LOW" in result
    
    def test_generate_affected_components_with_empty_list(self):
        """Test with empty impact analysis."""
        result = _generate_affected_components([])
        assert result == ""


class TestGenerateRequiredChanges:
    """Test suite for _generate_required_changes function."""
    
    def test_generate_required_changes_includes_all_details(self):
        """Test that all impact details are included."""
        impact_analysis = [
            {
                "file_path": "api/endpoints.py",
                "impact_type": "api_contract",
                "severity": "high",
                "description": "Critical API changes needed",
                "suggested_changes": ["Update endpoint signature", "Add validation"]
            }
        ]
        
        result = _generate_required_changes(impact_analysis)
        
        assert "api/endpoints.py" in result
        assert "Api Contract" in result
        assert "HIGH" in result
        assert "Critical API changes needed" in result
        assert "Update endpoint signature" in result
        assert "Add validation" in result
    
    def test_generate_required_changes_handles_multiple_files(self):
        """Test with multiple impacted files."""
        impact_analysis = [
            {
                "file_path": "file1.py",
                "impact_type": "business_logic",
                "severity": "medium",
                "description": "Changes needed",
                "suggested_changes": ["Change 1"]
            },
            {
                "file_path": "file2.py",
                "impact_type": "validation",
                "severity": "low",
                "description": "Minor updates",
                "suggested_changes": ["Change 2"]
            }
        ]
        
        result = _generate_required_changes(impact_analysis)
        
        assert "file1.py" in result
        assert "file2.py" in result


class TestCalculateEstimatedEffort:
    """Test suite for _calculate_estimated_effort function."""
    
    def test_calculate_effort_with_mixed_severities(self):
        """Test effort calculation with mixed severity levels."""
        impact_analysis = [
            {"severity": "high"},
            {"severity": "high"},
            {"severity": "medium"},
            {"severity": "low"}
        ]
        
        result = _calculate_estimated_effort(impact_analysis)
        
        # high=3, high=3, medium=2, low=1 = 9 points
        assert "9" in result
        assert "Total Effort Points" in result
        assert "High Severity: 2" in result
        assert "Medium Severity: 1" in result
        assert "Low Severity: 1" in result
    
    def test_calculate_effort_small_change(self):
        """Test effort calculation for small change."""
        impact_analysis = [
            {"severity": "low"},
            {"severity": "low"}
        ]
        
        result = _calculate_estimated_effort(impact_analysis)
        
        assert "2" in result
        assert "single sprint" in result.lower()
    
    def test_calculate_effort_large_change(self):
        """Test effort calculation for large change."""
        impact_analysis = [
            {"severity": "high"},
            {"severity": "high"},
            {"severity": "high"},
            {"severity": "high"},
            {"severity": "high"},
            {"severity": "high"}
        ]
        
        result = _calculate_estimated_effort(impact_analysis)
        
        assert "18" in result
        assert "large change" in result.lower()
    
    def test_calculate_effort_with_empty_list(self):
        """Test effort calculation with no impacts."""
        result = _calculate_estimated_effort([])
        
        assert "0" in result


class TestGenerateMinimalSpec:
    """Test suite for _generate_minimal_spec function."""
    
    def test_generate_minimal_spec_includes_title(self):
        """Test that minimal spec includes regulatory title."""
        regulatory_model = {
            "title": "Test Regulation",
            "description": "Test description"
        }
        
        result = _generate_minimal_spec(regulatory_model)
        
        assert "Test Regulation" in result
        assert "Test description" in result
        assert "No impacted components identified" in result
        assert "Manual analysis required" in result


class TestGenerateTechnicalSpec:
    """Test suite for _generate_technical_spec function."""
    
    @patch('backend.agents.spec_generator._generate_overview')
    @patch('backend.agents.spec_generator._generate_acceptance_criteria')
    def test_generate_technical_spec_structure(self, mock_criteria, mock_overview):
        """Test that technical spec has correct structure."""
        mock_overview.return_value = "Test overview"
        mock_criteria.return_value = "- Criterion 1\n- Criterion 2"
        
        regulatory_model = {
            "title": "Test Regulation",
            "description": "Test",
            "requirements": ["Req 1"],
            "deadlines": [],
            "affected_systems": ["Pix"]
        }
        
        impact_analysis = [
            {
                "file_path": "test.py",
                "impact_type": "business_logic",
                "severity": "medium",
                "description": "Test",
                "suggested_changes": ["Change 1"]
            }
        ]
        
        mock_llm = Mock()
        result = _generate_technical_spec(regulatory_model, impact_analysis, mock_llm)
        
        # Check all required sections are present
        assert "# Technical Specification: Test Regulation" in result
        assert "## Overview" in result
        assert "## Affected Components" in result
        assert "## Required Changes" in result
        assert "## Acceptance Criteria" in result
        assert "## Estimated Effort" in result
        assert "test.py" in result


class TestGenerateOverview:
    """Test suite for _generate_overview function."""
    
    def test_generate_overview_with_llm(self):
        """Test overview generation using LLM."""
        mock_llm = Mock()
        mock_llm.generate.return_value = "This is a comprehensive overview of the regulatory change."
        
        regulatory_model = {
            "title": "Test Regulation",
            "description": "Detailed description",
            "requirements": ["Req 1", "Req 2"],
            "deadlines": [{"date": "2024-12-31", "description": "Deadline"}],
            "affected_systems": ["Pix", "Payments"]
        }
        
        result = _generate_overview(regulatory_model, mock_llm)
        
        assert "comprehensive overview" in result
        mock_llm.generate.assert_called_once()
    
    def test_generate_overview_llm_failure(self):
        """Test overview generation when LLM fails."""
        mock_llm = Mock()
        mock_llm.generate.side_effect = Exception("LLM error")
        
        regulatory_model = {
            "title": "Test",
            "description": "Fallback description",
            "requirements": [],
            "deadlines": [],
            "affected_systems": ["Pix"]
        }
        
        result = _generate_overview(regulatory_model, mock_llm)
        
        # Should fallback to description
        assert "Fallback description" in result
        assert "Pix" in result


class TestGenerateAcceptanceCriteria:
    """Test suite for _generate_acceptance_criteria function."""
    
    def test_generate_acceptance_criteria_with_llm(self):
        """Test acceptance criteria generation using LLM."""
        mock_llm = Mock()
        mock_llm.generate.return_value = """
- O sistema DEVE validar todos os campos obrigatórios
- O sistema DEVE retornar erro para dados inválidos
- O sistema DEVE manter compatibilidade com versão anterior
"""
        
        regulatory_model = {
            "requirements": ["Add validation", "Maintain compatibility"]
        }
        
        result = _generate_acceptance_criteria(regulatory_model, mock_llm)
        
        assert "validar todos os campos" in result
        assert result.startswith("-")
        mock_llm.generate.assert_called_once()
    
    def test_generate_acceptance_criteria_no_requirements(self):
        """Test with no requirements."""
        mock_llm = Mock()
        regulatory_model = {"requirements": []}
        
        result = _generate_acceptance_criteria(regulatory_model, mock_llm)
        
        assert "reviewed and tested" in result
    
    def test_generate_acceptance_criteria_llm_failure(self):
        """Test fallback when LLM fails."""
        mock_llm = Mock()
        mock_llm.generate.side_effect = Exception("LLM error")
        
        regulatory_model = {
            "requirements": ["Requirement 1", "Requirement 2"]
        }
        
        result = _generate_acceptance_criteria(regulatory_model, mock_llm)
        
        # Should create fallback criteria
        assert "Requirement 1" in result
        assert "Requirement 2" in result
        assert result.startswith("-")
