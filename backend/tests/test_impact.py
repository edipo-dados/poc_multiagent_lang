"""
Unit tests for Impact Agent.

Tests the Impact Agent's ability to analyze code files and generate
technical impact assessments based on regulatory changes.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from backend.agents.impact import (
    impact_agent,
    _load_file_content,
    _classify_impact_type,
    _analyze_file_impact,
    _parse_impact_response,
    _create_fallback_impact
)
from backend.models.state import GlobalState
from backend.models.impact import Impact


class TestImpactAgent:
    """Test suite for the main impact_agent function."""
    
    def test_impact_agent_with_no_impacted_files(self):
        """Test that agent handles empty impacted_files list."""
        state = GlobalState(
            raw_regulatory_text="Test regulation",
            regulatory_model={
                "title": "Test Regulation",
                "description": "Test description",
                "requirements": ["Req 1"],
                "deadlines": [],
                "affected_systems": ["Pix"]
            },
            impacted_files=[],
            execution_id="test-123"
        )
        
        result = impact_agent(state)
        
        assert result.impact_analysis == []
        assert result.error is None
    
    def test_impact_agent_without_regulatory_model(self):
        """Test that agent raises error when regulatory_model is missing."""
        state = GlobalState(
            raw_regulatory_text="Test regulation",
            impacted_files=[{"file_path": "test.py"}],
            execution_id="test-123"
        )
        
        with pytest.raises(ValueError, match="regulatory_model is required"):
            impact_agent(state)
    
    @patch('backend.agents.impact.get_llm')
    @patch('backend.agents.impact._load_file_content')
    def test_impact_agent_analyzes_files(self, mock_load, mock_get_llm):
        """Test that agent analyzes each impacted file."""
        # Setup mocks
        mock_load.return_value = "def test(): pass"
        mock_llm = Mock()
        mock_llm.generate.return_value = """
SEVERIDADE: HIGH
DESCRIÇÃO: Critical changes needed
MUDANÇAS:
- Update function signature
- Add validation logic
- Update tests
"""
        mock_get_llm.return_value = mock_llm
        
        state = GlobalState(
            raw_regulatory_text="Test regulation",
            regulatory_model={
                "title": "Test Regulation",
                "description": "Test description",
                "requirements": ["Req 1", "Req 2"],
                "deadlines": [],
                "affected_systems": ["Pix"]
            },
            impacted_files=[
                {"file_path": "api/endpoints.py", "relevance_score": 0.9},
                {"file_path": "domain/validators.py", "relevance_score": 0.8}
            ],
            execution_id="test-123"
        )
        
        result = impact_agent(state)
        
        assert len(result.impact_analysis) == 2
        assert result.impact_analysis[0]["file_path"] == "api/endpoints.py"
        assert result.impact_analysis[0]["impact_type"] == "api_contract"
        assert result.impact_analysis[1]["file_path"] == "domain/validators.py"
        assert result.impact_analysis[1]["impact_type"] == "validation"
        assert result.error is None
    
    @patch('backend.agents.impact.get_llm')
    @patch('backend.agents.impact._load_file_content')
    def test_impact_agent_continues_on_file_error(self, mock_load, mock_get_llm):
        """Test that agent continues analyzing other files if one fails."""
        # Setup mocks - first file fails, second succeeds
        mock_load.side_effect = [
            FileNotFoundError("File not found"),
            "def test(): pass"
        ]
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
                {"file_path": "missing.py"},
                {"file_path": "existing.py"}
            ],
            execution_id="test-123"
        )
        
        result = impact_agent(state)
        
        # Should have analyzed only the second file
        assert len(result.impact_analysis) == 1
        assert result.impact_analysis[0]["file_path"] == "existing.py"


class TestLoadFileContent:
    """Test suite for _load_file_content function."""
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.read_text')
    def test_load_file_content_success(self, mock_read, mock_is_file, mock_exists):
        """Test successful file loading."""
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_read.return_value = "file content"
        
        content = _load_file_content("fake_pix_repo", "test.py")
        
        assert content == "file content"
    
    @patch('pathlib.Path.exists')
    def test_load_file_content_not_found(self, mock_exists):
        """Test error when file doesn't exist."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            _load_file_content("fake_pix_repo", "missing.py")
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    def test_load_file_content_not_a_file(self, mock_is_file, mock_exists):
        """Test error when path is not a file."""
        mock_exists.return_value = True
        mock_is_file.return_value = False
        
        with pytest.raises(IOError, match="not a file"):
            _load_file_content("fake_pix_repo", "directory")


class TestClassifyImpactType:
    """Test suite for _classify_impact_type function."""
    
    def test_classify_schema_change(self):
        """Test classification of database model files."""
        impact_type = _classify_impact_type("database/models.py", "class User(Base):")
        assert impact_type == "schema_change"
    
    def test_classify_validation(self):
        """Test classification of validator files."""
        impact_type = _classify_impact_type("domain/validators.py", "def validate():")
        assert impact_type == "validation"
    
    def test_classify_api_contract_endpoints(self):
        """Test classification of API endpoint files."""
        impact_type = _classify_impact_type("api/endpoints.py", "@router.post")
        assert impact_type == "api_contract"
    
    def test_classify_api_contract_schemas(self):
        """Test classification of API schema files."""
        impact_type = _classify_impact_type("api/schemas.py", "class Schema(BaseModel):")
        assert impact_type == "api_contract"
    
    def test_classify_business_logic_services(self):
        """Test classification of service files."""
        impact_type = _classify_impact_type("services/pix_service.py", "def process():")
        assert impact_type == "business_logic"
    
    def test_classify_business_logic_domain(self):
        """Test classification of domain files."""
        impact_type = _classify_impact_type("domain/models.py", "class Pix:")
        assert impact_type == "business_logic"
    
    def test_classify_default_business_logic(self):
        """Test default classification for unknown files."""
        impact_type = _classify_impact_type("utils/helper.py", "def helper():")
        assert impact_type == "business_logic"


class TestParseImpactResponse:
    """Test suite for _parse_impact_response function."""
    
    def test_parse_complete_response(self):
        """Test parsing a complete LLM response."""
        response = """
SEVERIDADE: HIGH
DESCRIÇÃO: This file needs critical updates to comply with new regulations.
MUDANÇAS:
- Update validation rules
- Add new fields to schema
- Implement compliance checks
"""
        severity, description, changes = _parse_impact_response(response)
        
        assert severity == "high"
        assert "critical updates" in description
        assert len(changes) == 3
        assert "Update validation rules" in changes
    
    def test_parse_response_with_portuguese_keywords(self):
        """Test parsing response with Portuguese keywords."""
        response = """
SEVERIDADE: MÉDIO
DESCRIÇÃO: Mudanças moderadas necessárias
MUDANÇAS:
- Atualizar lógica
- Adicionar validação
"""
        severity, description, changes = _parse_impact_response(response)
        
        assert severity == "medium"
        assert "moderadas" in description
        assert len(changes) == 2
    
    def test_parse_response_with_low_severity(self):
        """Test parsing response with low severity."""
        response = """
SEVERIDADE: LOW
DESCRIÇÃO: Minor changes needed
MUDANÇAS:
- Update documentation
"""
        severity, description, changes = _parse_impact_response(response)
        
        assert severity == "low"
        assert len(changes) == 1
    
    def test_parse_incomplete_response(self):
        """Test parsing incomplete response with defaults."""
        response = "Some random text without proper format"
        
        severity, description, changes = _parse_impact_response(response)
        
        # Should return defaults
        assert severity == "medium"
        assert len(changes) >= 1  # At least one default change
    
    def test_parse_response_with_multiline_description(self):
        """Test parsing response with multi-line description."""
        response = """
SEVERIDADE: HIGH
DESCRIÇÃO: This is a long description
that spans multiple lines
and provides detailed context.
MUDANÇAS:
- Change 1
"""
        severity, description, changes = _parse_impact_response(response)
        
        assert severity == "high"
        assert "long description" in description
        assert "multiple lines" in description


class TestCreateFallbackImpact:
    """Test suite for _create_fallback_impact function."""
    
    def test_create_fallback_for_schema_change(self):
        """Test fallback impact for schema change."""
        regulatory_model = {
            "title": "Test Regulation",
            "description": "Test",
            "requirements": ["Req 1"],
            "deadlines": [],
            "affected_systems": ["Pix"]
        }
        
        impact = _create_fallback_impact("database/models.py", "schema_change", regulatory_model)
        
        assert impact.file_path == "database/models.py"
        assert impact.impact_type == "schema_change"
        assert impact.severity == "medium"
        assert "schema" in impact.description.lower()
        assert len(impact.suggested_changes) > 0
    
    def test_create_fallback_for_validation(self):
        """Test fallback impact for validation."""
        regulatory_model = {
            "title": "Test",
            "description": "Test",
            "requirements": [],
            "deadlines": [],
            "affected_systems": []
        }
        
        impact = _create_fallback_impact("validators.py", "validation", regulatory_model)
        
        assert impact.impact_type == "validation"
        assert "validation" in impact.description.lower()


class TestAnalyzeFileImpact:
    """Test suite for _analyze_file_impact function."""
    
    @patch('backend.agents.impact.get_llm')
    def test_analyze_file_impact_with_llm(self, mock_get_llm):
        """Test file impact analysis using LLM."""
        mock_llm = Mock()
        mock_llm.generate.return_value = """
SEVERIDADE: HIGH
DESCRIÇÃO: Critical API changes required
MUDANÇAS:
- Update endpoint signature
- Add new validation
- Update response schema
"""
        
        regulatory_model = {
            "title": "New API Requirements",
            "description": "API must support new fields",
            "requirements": ["Add field X", "Validate field Y"],
            "deadlines": [],
            "affected_systems": ["Pix API"]
        }
        
        impact = _analyze_file_impact(
            file_path="api/endpoints.py",
            content="@router.post('/pix')\ndef create_pix():\n    pass",
            regulatory_model=regulatory_model,
            llm=mock_llm
        )
        
        assert impact.file_path == "api/endpoints.py"
        assert impact.impact_type == "api_contract"
        assert impact.severity == "high"
        assert len(impact.suggested_changes) == 3
    
    @patch('backend.agents.impact.get_llm')
    def test_analyze_file_impact_llm_failure(self, mock_get_llm):
        """Test fallback when LLM fails."""
        mock_llm = Mock()
        mock_llm.generate.side_effect = Exception("LLM error")
        
        regulatory_model = {
            "title": "Test",
            "description": "Test",
            "requirements": ["Req 1"],
            "deadlines": [],
            "affected_systems": ["Pix"]
        }
        
        impact = _analyze_file_impact(
            file_path="services/pix_service.py",
            content="def process_pix(): pass",
            regulatory_model=regulatory_model,
            llm=mock_llm
        )
        
        # Should return fallback impact
        assert impact.file_path == "services/pix_service.py"
        assert impact.impact_type == "business_logic"
        assert impact.severity == "medium"
        assert len(impact.suggested_changes) > 0
