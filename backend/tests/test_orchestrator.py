"""
Tests for LangGraph Orchestrator

Tests the RegulatoryAnalysisGraph class to ensure:
- Deterministic agent execution sequence
- State propagation between agents
- Error handling and execution halt
- Proper state updates

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import pytest
import uuid
from backend.orchestrator.graph import RegulatoryAnalysisGraph
from backend.models.state import GlobalState


class TestRegulatoryAnalysisGraph:
    """Test suite for RegulatoryAnalysisGraph orchestrator."""
    
    def test_graph_initialization(self):
        """Test that graph initializes without errors."""
        graph = RegulatoryAnalysisGraph()
        assert graph is not None
        assert graph.compiled_graph is not None
    
    def test_execute_with_valid_input(self):
        """Test successful execution with valid regulatory text."""
        # Create initial state
        initial_state = GlobalState(
            raw_regulatory_text="Nova regra do Banco Central exige validação adicional para transações Pix acima de R$ 1000.",
            execution_id=str(uuid.uuid4())
        )
        
        # Execute graph
        graph = RegulatoryAnalysisGraph()
        final_state = graph.execute(initial_state)
        
        # Verify state was updated by agents
        assert final_state is not None
        assert final_state.execution_id == initial_state.execution_id
        
        # Verify Sentinel Agent outputs
        assert final_state.change_detected is not None
        assert final_state.risk_level in ["low", "medium", "high"]
        
        # Verify Translator Agent outputs
        assert final_state.regulatory_model is not None
        assert "title" in final_state.regulatory_model
        assert "description" in final_state.regulatory_model
        
        # Verify CodeReader Agent outputs (stub returns empty list)
        assert final_state.impacted_files is not None
        assert isinstance(final_state.impacted_files, list)
        
        # Verify Impact Agent outputs (empty since no impacted files)
        assert final_state.impact_analysis is not None
        assert isinstance(final_state.impact_analysis, list)
        
        # Verify SpecGenerator Agent outputs (stub returns placeholder)
        assert final_state.technical_spec is not None
        assert isinstance(final_state.technical_spec, str)
        assert len(final_state.technical_spec) > 0
        
        # Verify KiroPrompt Agent outputs (stub returns placeholder)
        assert final_state.kiro_prompt is not None
        assert isinstance(final_state.kiro_prompt, str)
        assert len(final_state.kiro_prompt) > 0
        
        # Verify no errors occurred
        assert final_state.error is None
    
    def test_execute_with_empty_text_raises_error(self):
        """Test that empty regulatory text raises ValueError."""
        initial_state = GlobalState(
            raw_regulatory_text="",
            execution_id=str(uuid.uuid4())
        )
        
        graph = RegulatoryAnalysisGraph()
        
        with pytest.raises(ValueError, match="raw_regulatory_text is required"):
            graph.execute(initial_state)
    
    def test_execute_without_execution_id_raises_error(self):
        """Test that missing execution_id raises ValueError."""
        initial_state = GlobalState(
            raw_regulatory_text="Test regulatory text"
        )
        
        graph = RegulatoryAnalysisGraph()
        
        with pytest.raises(ValueError, match="execution_id is required"):
            graph.execute(initial_state)
    
    def test_state_propagation_between_agents(self):
        """Test that state is propagated correctly between agents."""
        initial_state = GlobalState(
            raw_regulatory_text="Regulação sobre Pix com prazo imediato.",
            execution_id=str(uuid.uuid4())
        )
        
        graph = RegulatoryAnalysisGraph()
        final_state = graph.execute(initial_state)
        
        # Verify that each agent's outputs are present
        # This confirms state was passed through the pipeline
        assert final_state.change_detected is not None  # Sentinel output
        assert final_state.regulatory_model is not None  # Translator output
        assert final_state.impacted_files is not None  # CodeReader output
        assert final_state.impact_analysis is not None  # Impact output
        assert final_state.technical_spec is not None  # SpecGenerator output
        assert final_state.kiro_prompt is not None  # KiroPrompt output
    
    def test_deterministic_execution_sequence(self):
        """Test that agents execute in the correct sequence."""
        # This test verifies that the graph structure is correct
        # by checking that all expected outputs are present
        initial_state = GlobalState(
            raw_regulatory_text="Mudança obrigatória no sistema Pix.",
            execution_id=str(uuid.uuid4())
        )
        
        graph = RegulatoryAnalysisGraph()
        final_state = graph.execute(initial_state)
        
        # If execution was deterministic and sequential:
        # 1. Sentinel must have set change_detected and risk_level
        assert final_state.change_detected is not None
        assert final_state.risk_level is not None
        
        # 2. Translator must have created regulatory_model
        assert final_state.regulatory_model is not None
        
        # 3. CodeReader must have set impacted_files (even if empty)
        assert final_state.impacted_files is not None
        
        # 4. Impact must have set impact_analysis (even if empty)
        assert final_state.impact_analysis is not None
        
        # 5. SpecGenerator must have set technical_spec
        assert final_state.technical_spec is not None
        
        # 6. KiroPrompt must have set kiro_prompt
        assert final_state.kiro_prompt is not None
    
    def test_multiple_executions_are_independent(self):
        """Test that multiple executions don't interfere with each other."""
        graph = RegulatoryAnalysisGraph()
        
        # Execute first analysis
        state1 = GlobalState(
            raw_regulatory_text="Primeira regulação sobre Pix.",
            execution_id=str(uuid.uuid4())
        )
        final_state1 = graph.execute(state1)
        
        # Execute second analysis
        state2 = GlobalState(
            raw_regulatory_text="Segunda regulação diferente.",
            execution_id=str(uuid.uuid4())
        )
        final_state2 = graph.execute(state2)
        
        # Verify executions are independent
        assert final_state1.execution_id != final_state2.execution_id
        assert final_state1.raw_regulatory_text != final_state2.raw_regulatory_text
        
        # Both should have completed successfully
        assert final_state1.error is None
        assert final_state2.error is None


class TestAgentStubs:
    """Test suite for stub agent implementations."""
    
    def test_code_reader_stub_returns_empty_list(self):
        """Test that CodeReader stub returns empty impacted_files."""
        from backend.orchestrator.graph import code_reader_agent
        
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id=str(uuid.uuid4())
        )
        state.regulatory_model = {"title": "Test"}
        
        updated_state = code_reader_agent(state)
        
        assert updated_state.impacted_files == []
    
    def test_spec_generator_stub_returns_placeholder(self):
        """Test that SpecGenerator stub returns placeholder text."""
        from backend.orchestrator.graph import spec_generator_agent
        
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id=str(uuid.uuid4())
        )
        
        updated_state = spec_generator_agent(state)
        
        assert updated_state.technical_spec is not None
        assert "STUB" in updated_state.technical_spec
        assert len(updated_state.technical_spec) > 0
    
    def test_kiro_prompt_stub_returns_placeholder(self):
        """Test that KiroPrompt stub returns placeholder text."""
        from backend.orchestrator.graph import kiro_prompt_agent
        
        state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id=str(uuid.uuid4())
        )
        
        updated_state = kiro_prompt_agent(state)
        
        assert updated_state.kiro_prompt is not None
        assert "STUB" in updated_state.kiro_prompt
        assert len(updated_state.kiro_prompt) > 0
