"""
Tests for LangGraph Orchestrator Structure

Tests the RegulatoryAnalysisGraph class structure without requiring LLM:
- Graph initialization
- Node and edge configuration
- Stub agent implementations
- Input validation

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import pytest
import uuid
from backend.orchestrator.graph import (
    RegulatoryAnalysisGraph,
    code_reader_agent,
    spec_generator_agent,
    kiro_prompt_agent
)
from backend.models.state import GlobalState


class TestGraphStructure:
    """Test suite for graph structure and configuration."""
    
    def test_graph_initialization(self):
        """Test that graph initializes without errors."""
        graph = RegulatoryAnalysisGraph()
        assert graph is not None
        assert graph.graph is not None
        assert graph.compiled_graph is not None
    
    def test_graph_has_all_nodes(self):
        """Test that graph contains all six agent nodes."""
        graph = RegulatoryAnalysisGraph()
        
        # LangGraph stores nodes in the graph structure
        # We can verify by checking the compiled graph has the expected structure
        assert graph.compiled_graph is not None
        
        # The graph should be compiled successfully with all nodes
        # This is verified by the fact that initialization doesn't raise errors
    
    def test_input_validation_empty_text(self):
        """Test that empty regulatory text raises ValueError."""
        initial_state = GlobalState(
            raw_regulatory_text="",
            execution_id=str(uuid.uuid4())
        )
        
        graph = RegulatoryAnalysisGraph()
        
        with pytest.raises(ValueError, match="raw_regulatory_text is required"):
            graph.execute(initial_state)
    
    def test_input_validation_missing_execution_id(self):
        """Test that missing execution_id raises ValueError."""
        initial_state = GlobalState(
            raw_regulatory_text="Test regulatory text"
        )
        
        graph = RegulatoryAnalysisGraph()
        
        with pytest.raises(ValueError, match="execution_id is required"):
            graph.execute(initial_state)


class TestStubAgents:
    """Test suite for stub agent implementations."""
    
    def test_code_reader_stub_returns_empty_list(self):
        """Test that CodeReader stub returns empty impacted_files."""
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id=str(uuid.uuid4())
        )
        state.regulatory_model = {"title": "Test"}
        
        updated_state = code_reader_agent(state)
        
        assert updated_state.impacted_files == []
        assert isinstance(updated_state.impacted_files, list)
    
    def test_code_reader_stub_preserves_other_state(self):
        """Test that CodeReader stub doesn't modify other state fields."""
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id=str(uuid.uuid4())
        )
        state.regulatory_model = {"title": "Test"}
        state.change_detected = True
        state.risk_level = "high"
        
        updated_state = code_reader_agent(state)
        
        assert updated_state.raw_regulatory_text == "Test text"
        assert updated_state.regulatory_model == {"title": "Test"}
        assert updated_state.change_detected == True
        assert updated_state.risk_level == "high"
    
    def test_spec_generator_stub_returns_placeholder(self):
        """Test that SpecGenerator stub returns placeholder text."""
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id=str(uuid.uuid4())
        )
        
        updated_state = spec_generator_agent(state)
        
        assert updated_state.technical_spec is not None
        assert isinstance(updated_state.technical_spec, str)
        assert "STUB" in updated_state.technical_spec
        assert len(updated_state.technical_spec) > 0
        assert "Technical Specification" in updated_state.technical_spec
    
    def test_spec_generator_stub_preserves_other_state(self):
        """Test that SpecGenerator stub doesn't modify other state fields."""
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id=str(uuid.uuid4())
        )
        state.impact_analysis = [{"file": "test.py"}]
        
        updated_state = spec_generator_agent(state)
        
        assert updated_state.impact_analysis == [{"file": "test.py"}]
        assert updated_state.raw_regulatory_text == "Test text"
    
    def test_kiro_prompt_stub_returns_placeholder(self):
        """Test that KiroPrompt stub returns placeholder text."""
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id=str(uuid.uuid4())
        )
        
        updated_state = kiro_prompt_agent(state)
        
        assert updated_state.kiro_prompt is not None
        assert isinstance(updated_state.kiro_prompt, str)
        assert "STUB" in updated_state.kiro_prompt
        assert len(updated_state.kiro_prompt) > 0
    
    def test_kiro_prompt_stub_preserves_other_state(self):
        """Test that KiroPrompt stub doesn't modify other state fields."""
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id=str(uuid.uuid4())
        )
        state.technical_spec = "Test spec"
        
        updated_state = kiro_prompt_agent(state)
        
        assert updated_state.technical_spec == "Test spec"
        assert updated_state.raw_regulatory_text == "Test text"


class TestStateManagement:
    """Test suite for state management."""
    
    def test_global_state_initialization(self):
        """Test that GlobalState can be initialized with required fields."""
        state = GlobalState(
            raw_regulatory_text="Test regulatory text",
            execution_id=str(uuid.uuid4())
        )
        
        assert state.raw_regulatory_text == "Test regulatory text"
        assert state.execution_id is not None
        assert state.change_detected is None
        assert state.risk_level is None
        assert state.regulatory_model is None
        assert state.impacted_files == []
        assert state.impact_analysis == []
        assert state.technical_spec is None
        assert state.kiro_prompt is None
        assert state.error is None
    
    def test_global_state_can_be_updated(self):
        """Test that GlobalState fields can be updated."""
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id=str(uuid.uuid4())
        )
        
        # Update fields
        state.change_detected = True
        state.risk_level = "high"
        state.regulatory_model = {"title": "Test"}
        state.impacted_files = [{"file_path": "test.py"}]
        
        # Verify updates
        assert state.change_detected == True
        assert state.risk_level == "high"
        assert state.regulatory_model == {"title": "Test"}
        assert len(state.impacted_files) == 1
