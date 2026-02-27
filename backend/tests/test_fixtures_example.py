"""
Example tests demonstrating how to use the test fixtures.

This file shows various patterns for using the fixtures in tests.
"""

import pytest
from backend.models.state import GlobalState
from backend.models.regulatory import RegulatoryModel
from backend.models.impact import ImpactedFile, Impact
from backend.tests.fixtures import (
    SHORT_REGULATION,
    MEDIUM_REGULATION,
    ALL_REGULATORY_TEXTS,
    MOCK_SENTINEL_RESPONSE,
    MOCK_TRANSLATOR_RESPONSE,
    MOCK_CODEREADER_RESPONSE,
    MOCK_IMPACT_RESPONSE,
    MOCK_COMPLETE_STATE,
)


class TestRegulatoryTexts:
    """Examples of using regulatory text fixtures."""
    
    def test_short_regulation_is_valid(self):
        """Test that short regulation text is not empty."""
        assert len(SHORT_REGULATION) > 0
        assert "BCB" in SHORT_REGULATION
        assert "Pix" in SHORT_REGULATION
    
    def test_all_regulatory_texts_are_portuguese(self):
        """Test that all texts contain Portuguese regulatory keywords."""
        for name, text in ALL_REGULATORY_TEXTS.items():
            assert len(text) > 0
            # Check for common Portuguese regulatory terms
            assert any(word in text for word in ["Art.", "Banco Central", "Resolução", "RESOLUÇÃO"])


class TestMockResponses:
    """Examples of using mock response fixtures."""
    
    def test_sentinel_response_structure(self):
        """Test that sentinel mock response has expected structure."""
        assert "change_detected" in MOCK_SENTINEL_RESPONSE
        assert "risk_level" in MOCK_SENTINEL_RESPONSE
        assert MOCK_SENTINEL_RESPONSE["change_detected"] is True
        assert MOCK_SENTINEL_RESPONSE["risk_level"] in ["low", "medium", "high"]
    
    def test_translator_response_creates_model(self):
        """Test that translator mock can create RegulatoryModel."""
        model = RegulatoryModel(**MOCK_TRANSLATOR_RESPONSE)
        assert model.title is not None
        assert len(model.requirements) > 0
        assert len(model.deadlines) > 0
        assert len(model.affected_systems) > 0
    
    def test_codereader_response_creates_impacted_files(self):
        """Test that codereader mock can create ImpactedFile objects."""
        files = [ImpactedFile(**item) for item in MOCK_CODEREADER_RESPONSE]
        assert len(files) > 0
        for file in files:
            assert file.file_path.startswith("fake_pix_repo/")
            assert 0.0 <= file.relevance_score <= 1.0
            assert len(file.snippet) > 0
    
    def test_impact_response_creates_impact_objects(self):
        """Test that impact mock can create Impact objects."""
        impacts = [Impact(**item) for item in MOCK_IMPACT_RESPONSE]
        assert len(impacts) > 0
        for impact in impacts:
            assert impact.file_path is not None
            assert impact.impact_type in ["schema_change", "business_logic", "validation", "api_contract"]
            assert impact.severity in ["low", "medium", "high"]
            assert len(impact.suggested_changes) > 0


class TestCompleteState:
    """Examples of using complete state fixtures."""
    
    def test_complete_state_creates_global_state(self):
        """Test that complete state mock can create GlobalState."""
        state = GlobalState(**MOCK_COMPLETE_STATE)
        assert state.raw_regulatory_text is not None
        assert state.change_detected is True
        assert state.risk_level == "high"
        assert state.regulatory_model is not None
        assert len(state.impacted_files) > 0
        assert len(state.impact_analysis) > 0
        assert state.technical_spec is not None
        assert state.kiro_prompt is not None
    
    def test_complete_state_has_all_agent_outputs(self):
        """Test that complete state includes outputs from all agents."""
        state = GlobalState(**MOCK_COMPLETE_STATE)
        # Sentinel outputs
        assert state.change_detected is not None
        assert state.risk_level is not None
        # Translator outputs
        assert state.regulatory_model is not None
        # CodeReader outputs
        assert len(state.impacted_files) > 0
        # Impact outputs
        assert len(state.impact_analysis) > 0
        # SpecGenerator outputs
        assert state.technical_spec is not None
        # KiroPrompt outputs
        assert state.kiro_prompt is not None


class TestFixtureIntegration:
    """Examples of using fixtures together in integration tests."""
    
    def test_pipeline_with_fixtures(self):
        """Test a simplified pipeline using fixtures."""
        # Start with regulatory text
        text = SHORT_REGULATION
        assert len(text) > 0
        
        # Simulate Sentinel response
        sentinel_result = MOCK_SENTINEL_RESPONSE
        assert sentinel_result["change_detected"] is True
        
        # Simulate Translator response
        regulatory_model = RegulatoryModel(**MOCK_TRANSLATOR_RESPONSE)
        assert len(regulatory_model.requirements) > 0
        
        # Simulate CodeReader response
        impacted_files = [ImpactedFile(**item) for item in MOCK_CODEREADER_RESPONSE]
        assert len(impacted_files) > 0
        
        # Simulate Impact response
        impacts = [Impact(**item) for item in MOCK_IMPACT_RESPONSE]
        assert len(impacts) > 0
        
        # All steps completed successfully
        assert True
    
    @pytest.mark.parametrize("text_name,text", ALL_REGULATORY_TEXTS.items())
    def test_all_texts_are_processable(self, text_name, text):
        """Test that all regulatory texts can be processed."""
        # This is a simple example - in real tests you'd process through agents
        assert len(text) > 0
        assert isinstance(text, str)
        # Verify it's in Portuguese (contains common Portuguese words)
        portuguese_indicators = ["o", "a", "de", "do", "da", "em", "para"]
        assert any(word in text.lower() for word in portuguese_indicators)
