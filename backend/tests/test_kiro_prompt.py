"""
Unit tests for KiroPrompt Agent.

Tests the KiroPrompt Agent's ability to generate development prompts
from regulatory models, impact analysis, and technical specifications.
"""

import pytest
from backend.agents.kiro_prompt import (
    kiro_prompt_agent,
    _generate_kiro_prompt,
    _generate_context,
    _generate_objective,
    _generate_specific_instructions,
    _generate_file_modifications,
    _generate_validation_steps,
    _extract_acceptance_criteria,
    _generate_constraints
)
from backend.models.state import GlobalState


class TestKiroPromptAgent:
    """Test suite for the main kiro_prompt_agent function."""
    
    def test_kiro_prompt_agent_without_regulatory_model(self):
        """Test that agent raises error when regulatory_model is missing."""
        state = GlobalState(
            raw_regulatory_text="Test regulation",
            impact_analysis=[],
            execution_id="test-123"
        )
        
        with pytest.raises(ValueError, match="regulatory_model is required"):
            kiro_prompt_agent(state)
    
    def test_kiro_prompt_agent_with_minimal_data(self):
        """Test that agent generates prompt with minimal data."""
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
            technical_spec=None,
            execution_id="test-123"
        )
        
        result = kiro_prompt_agent(state)
        
        assert result.kiro_prompt is not None
        assert "CONTEXT:" in result.kiro_prompt
        assert "OBJECTIVE:" in result.kiro_prompt
        assert "SPECIFIC INSTRUCTIONS:" in result.kiro_prompt
        assert "FILE MODIFICATIONS:" in result.kiro_prompt
        assert "VALIDATION STEPS:" in result.kiro_prompt
        assert "CONSTRAINTS:" in result.kiro_prompt
        assert "Test Regulation" in result.kiro_prompt
        assert result.error is None
    
    def test_kiro_prompt_agent_generates_complete_prompt(self):
        """Test that agent generates complete prompt with all data."""
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
            technical_spec="""# Technical Specification

## Acceptance Criteria
- Verify field validation is implemented
- Verify API schema is updated
- Run all tests
""",
            execution_id="test-123"
        )
        
        result = kiro_prompt_agent(state)
        
        assert result.kiro_prompt is not None
        assert "New Pix Requirements" in result.kiro_prompt
        assert "api/endpoints.py" in result.kiro_prompt
        assert "domain/validators.py" in result.kiro_prompt
        assert "Update endpoint" in result.kiro_prompt
        assert "Add new validator" in result.kiro_prompt
        assert "2024-12-31" in result.kiro_prompt
        assert result.error is None


class TestGenerateContext:
    """Test suite for _generate_context function."""
    
    def test_generate_context_with_all_fields(self):
        """Test context generation with all fields populated."""
        regulatory_model = {
            "title": "New Pix Requirements",
            "description": "Updated validation rules for Pix transactions",
            "requirements": ["Add field validation", "Update API schema"],
            "deadlines": [{"date": "2024-12-31", "description": "Implementation deadline"}],
            "affected_systems": ["Pix", "Payments"]
        }
        
        result = _generate_context(regulatory_model)
        
        assert "New Pix Requirements" in result
        assert "Updated validation rules" in result
        assert "Add field validation" in result
        assert "Update API schema" in result
        assert "2024-12-31" in result
        assert "Implementation deadline" in result
        assert "Pix, Payments" in result
    
    def test_generate_context_with_minimal_fields(self):
        """Test context generation with minimal fields."""
        regulatory_model = {
            "title": "Test",
            "description": "Test description",
            "requirements": [],
            "deadlines": [],
            "affected_systems": []
        }
        
        result = _generate_context(regulatory_model)
        
        assert "Test" in result
        assert "Test description" in result


class TestGenerateObjective:
    """Test suite for _generate_objective function."""
    
    def test_generate_objective_includes_title(self):
        """Test that objective includes regulatory title."""
        regulatory_model = {
            "title": "New Pix Requirements"
        }
        
        result = _generate_objective(regulatory_model)
        
        assert "New Pix Requirements" in result
        assert "Implement changes to comply" in result


class TestGenerateSpecificInstructions:
    """Test suite for _generate_specific_instructions function."""
    
    def test_generate_instructions_with_empty_analysis(self):
        """Test instruction generation with no impact analysis."""
        result = _generate_specific_instructions([])
        
        assert "Review regulatory requirements" in result
        assert "1." in result
    
    def test_generate_instructions_groups_by_type(self):
        """Test that instructions are grouped by impact type."""
        impact_analysis = [
            {
                "file_path": "api/endpoints.py",
                "impact_type": "api_contract",
                "severity": "high",
                "description": "API changes needed"
            },
            {
                "file_path": "domain/validators.py",
                "impact_type": "validation",
                "severity": "medium",
                "description": "Validation updates"
            }
        ]
        
        result = _generate_specific_instructions(impact_analysis)
        
        assert "API Contract Modifications" in result
        assert "Validation Rule Updates" in result
        assert "api/endpoints.py" in result
        assert "domain/validators.py" in result
        assert "[HIGH]" in result
        assert "[MEDIUM]" in result
    
    def test_generate_instructions_sorts_by_severity(self):
        """Test that instructions are sorted by severity (high first)."""
        impact_analysis = [
            {
                "file_path": "file1.py",
                "impact_type": "business_logic",
                "severity": "low",
                "description": "Low priority"
            },
            {
                "file_path": "file2.py",
                "impact_type": "business_logic",
                "severity": "high",
                "description": "High priority"
            },
            {
                "file_path": "file3.py",
                "impact_type": "business_logic",
                "severity": "medium",
                "description": "Medium priority"
            }
        ]
        
        result = _generate_specific_instructions(impact_analysis)
        
        # High should appear before medium and low
        high_pos = result.find("file2.py")
        medium_pos = result.find("file3.py")
        low_pos = result.find("file1.py")
        
        assert high_pos < medium_pos < low_pos
    
    def test_generate_instructions_includes_standard_steps(self):
        """Test that standard steps are included."""
        impact_analysis = [
            {
                "file_path": "test.py",
                "impact_type": "business_logic",
                "severity": "medium",
                "description": "Test"
            }
        ]
        
        result = _generate_specific_instructions(impact_analysis)
        
        assert "Run all existing tests" in result
        assert "Add new tests" in result
        assert "Update documentation" in result


class TestGenerateFileModifications:
    """Test suite for _generate_file_modifications function."""
    
    def test_generate_modifications_with_empty_analysis(self):
        """Test with no impact analysis."""
        result = _generate_file_modifications([])
        
        assert "No specific file modifications" in result
        assert "Manual analysis required" in result
    
    def test_generate_modifications_includes_all_details(self):
        """Test that all modification details are included."""
        impact_analysis = [
            {
                "file_path": "api/endpoints.py",
                "impact_type": "api_contract",
                "severity": "high",
                "suggested_changes": ["Update endpoint signature", "Add validation"]
            }
        ]
        
        result = _generate_file_modifications(impact_analysis)
        
        assert "api/endpoints.py" in result
        assert "api_contract" in result
        assert "high" in result
        assert "Update endpoint signature" in result
        assert "Add validation" in result
    
    def test_generate_modifications_handles_no_suggested_changes(self):
        """Test with impact that has no suggested changes."""
        impact_analysis = [
            {
                "file_path": "test.py",
                "impact_type": "business_logic",
                "severity": "medium",
                "suggested_changes": []
            }
        ]
        
        result = _generate_file_modifications(impact_analysis)
        
        assert "test.py" in result
        assert "Review and update as needed" in result


class TestGenerateValidationSteps:
    """Test suite for _generate_validation_steps function."""
    
    def test_generate_validation_with_technical_spec(self):
        """Test validation generation with technical spec."""
        technical_spec = """# Technical Specification

## Acceptance Criteria
- Verify field validation is implemented
- Verify API schema is updated
- Run all tests
"""
        regulatory_model = {
            "requirements": ["Req 1"]
        }
        
        result = _generate_validation_steps(technical_spec, regulatory_model)
        
        assert "Verify field validation is implemented" in result
        assert "Verify API schema is updated" in result
        assert "Run all tests" in result
        assert "Verify compliance with regulatory requirements" in result
    
    def test_generate_validation_without_technical_spec(self):
        """Test validation generation without technical spec."""
        regulatory_model = {
            "requirements": ["Add validation", "Update schema"]
        }
        
        result = _generate_validation_steps(None, regulatory_model)
        
        assert "Add validation" in result
        assert "Update schema" in result
        assert "Verify compliance" in result
    
    def test_generate_validation_includes_standard_steps(self):
        """Test that standard validation steps are included."""
        result = _generate_validation_steps(None, {"requirements": []})
        
        assert "Verify compliance with regulatory requirements" in result
        assert "Run existing test suite" in result
        assert "Perform manual testing" in result
        assert "Review changes with compliance team" in result


class TestExtractAcceptanceCriteria:
    """Test suite for _extract_acceptance_criteria function."""
    
    def test_extract_criteria_from_spec(self):
        """Test extracting criteria from technical spec."""
        technical_spec = """# Technical Specification

## Overview
Some overview text

## Acceptance Criteria
- Criterion 1
- Criterion 2
- Criterion 3

## Estimated Effort
Some effort text
"""
        
        result = _extract_acceptance_criteria(technical_spec)
        
        assert len(result) == 3
        assert "Criterion 1" in result
        assert "Criterion 2" in result
        assert "Criterion 3" in result
    
    def test_extract_criteria_no_section(self):
        """Test with spec that has no acceptance criteria section."""
        technical_spec = """# Technical Specification

## Overview
Some overview text
"""
        
        result = _extract_acceptance_criteria(technical_spec)
        
        assert len(result) == 0
    
    def test_extract_criteria_empty_section(self):
        """Test with empty acceptance criteria section."""
        technical_spec = """# Technical Specification

## Acceptance Criteria

## Estimated Effort
Some effort text
"""
        
        result = _extract_acceptance_criteria(technical_spec)
        
        assert len(result) == 0


class TestGenerateConstraints:
    """Test suite for _generate_constraints function."""
    
    def test_generate_constraints_includes_standard_items(self):
        """Test that standard constraints are included."""
        result = _generate_constraints()
        
        assert "backward compatibility" in result
        assert "code patterns" in result
        assert "documentation" in result
        assert "tested" in result
        assert "security" in result
        assert "performance" in result


class TestGenerateKiroPrompt:
    """Test suite for _generate_kiro_prompt function."""
    
    def test_generate_prompt_has_all_sections(self):
        """Test that generated prompt has all required sections."""
        regulatory_model = {
            "title": "Test Regulation",
            "description": "Test description",
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
        
        technical_spec = """## Acceptance Criteria
- Test criterion
"""
        
        result = _generate_kiro_prompt(regulatory_model, impact_analysis, technical_spec)
        
        assert "CONTEXT:" in result
        assert "OBJECTIVE:" in result
        assert "SPECIFIC INSTRUCTIONS:" in result
        assert "FILE MODIFICATIONS:" in result
        assert "VALIDATION STEPS:" in result
        assert "CONSTRAINTS:" in result
    
    def test_generate_prompt_references_source_data(self):
        """Test that prompt references data from regulatory model and impact analysis."""
        regulatory_model = {
            "title": "New Pix Requirements",
            "description": "Updated validation",
            "requirements": ["Add validation"],
            "deadlines": [],
            "affected_systems": ["Pix"]
        }
        
        impact_analysis = [
            {
                "file_path": "api/endpoints.py",
                "impact_type": "api_contract",
                "severity": "high",
                "description": "API changes",
                "suggested_changes": ["Update endpoint"]
            }
        ]
        
        result = _generate_kiro_prompt(regulatory_model, impact_analysis, None)
        
        # Should reference regulatory model
        assert "New Pix Requirements" in result
        assert "Add validation" in result
        
        # Should reference impact analysis
        assert "api/endpoints.py" in result
        assert "Update endpoint" in result
