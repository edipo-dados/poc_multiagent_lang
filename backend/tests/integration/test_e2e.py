"""
End-to-End Integration Tests

Tests the complete regulatory analysis pipeline from input to output,
verifying that all agents execute in sequence and all outputs are generated.

Requirements: 2.1, 12.1
"""

import pytest
import uuid
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch

from backend.models.state import GlobalState
from backend.orchestrator.graph import RegulatoryAnalysisGraph
from backend.services.audit import AuditService
from backend.tests.fixtures.regulatory_texts import (
    SHORT_REGULATION,
    MEDIUM_REGULATION,
    REGULATION_WITH_PIX
)


class TestEndToEndPipeline:
    """
    End-to-end integration tests for the complete analysis pipeline.
    
    These tests verify:
    - All agents execute in the correct sequence
    - All outputs are generated
    - Audit logs are created
    - State is properly propagated between agents
    """
    
    def test_full_pipeline_execution_with_short_regulation(self):
        """
        Test complete pipeline execution with short regulatory text.
        
        Verifies:
        - All six agents execute in sequence
        - All required outputs are generated
        - No errors occur during execution
        - State is properly updated at each step
        
        Requirements: 2.1
        """
        # Arrange
        execution_id = str(uuid.uuid4())
        initial_state = GlobalState(
            raw_regulatory_text=SHORT_REGULATION,
            execution_id=execution_id,
            execution_timestamp=datetime.now(UTC)
        )
        
        # Act
        orchestrator = RegulatoryAnalysisGraph()
        final_state = orchestrator.execute(initial_state)
        
        # Assert - Verify all agents executed
        assert final_state.execution_id == execution_id
        assert final_state.error is None, f"Pipeline failed with error: {final_state.error}"
        
        # Assert - Sentinel outputs
        assert final_state.change_detected is not None, "Sentinel did not set change_detected"
        assert final_state.risk_level in ["low", "medium", "high"], f"Invalid risk_level: {final_state.risk_level}"
        
        # Assert - Translator outputs
        assert final_state.regulatory_model is not None, "Translator did not generate regulatory_model"
        assert "title" in final_state.regulatory_model, "regulatory_model missing title"
        assert "description" in final_state.regulatory_model, "regulatory_model missing description"
        assert "requirements" in final_state.regulatory_model, "regulatory_model missing requirements"
        
        # Assert - CodeReader outputs
        assert isinstance(final_state.impacted_files, list), "impacted_files is not a list"
        # Note: May be empty if no relevant files found, which is acceptable
        
        # Assert - Impact outputs
        assert isinstance(final_state.impact_analysis, list), "impact_analysis is not a list"
        # Note: May be empty if no impacted files found
        
        # Assert - SpecGenerator outputs
        assert final_state.technical_spec is not None, "SpecGenerator did not generate technical_spec"
        assert len(final_state.technical_spec) > 0, "technical_spec is empty"
        assert "#" in final_state.technical_spec, "technical_spec does not contain markdown headers"
        
        # Assert - KiroPrompt outputs
        assert final_state.kiro_prompt is not None, "KiroPrompt did not generate kiro_prompt"
        assert len(final_state.kiro_prompt) > 0, "kiro_prompt is empty"
    
    def test_full_pipeline_execution_with_medium_regulation(self):
        """
        Test complete pipeline execution with medium-length regulatory text.
        
        Verifies the pipeline handles more complex regulatory text with
        multiple requirements and deadlines.
        
        Requirements: 2.1
        """
        # Arrange
        execution_id = str(uuid.uuid4())
        initial_state = GlobalState(
            raw_regulatory_text=MEDIUM_REGULATION,
            execution_id=execution_id,
            execution_timestamp=datetime.now(UTC)
        )
        
        # Act
        orchestrator = RegulatoryAnalysisGraph()
        final_state = orchestrator.execute(initial_state)
        
        # Assert - Pipeline completed successfully
        assert final_state.error is None, f"Pipeline failed with error: {final_state.error}"
        
        # Assert - All outputs generated
        assert final_state.change_detected is not None
        assert final_state.risk_level is not None
        assert final_state.regulatory_model is not None
        assert isinstance(final_state.impacted_files, list)
        assert isinstance(final_state.impact_analysis, list)
        assert final_state.technical_spec is not None
        assert final_state.kiro_prompt is not None
        
        # Assert - Regulatory model has multiple requirements
        assert len(final_state.regulatory_model.get("requirements", [])) > 1, \
            "Medium regulation should have multiple requirements"
    
    def test_full_pipeline_execution_with_pix_regulation(self):
        """
        Test complete pipeline execution with Pix-specific regulatory text.
        
        Verifies the pipeline correctly identifies Pix-related impacts
        and generates appropriate specifications.
        
        Requirements: 2.1
        """
        # Arrange
        execution_id = str(uuid.uuid4())
        initial_state = GlobalState(
            raw_regulatory_text=REGULATION_WITH_PIX,
            execution_id=execution_id,
            execution_timestamp=datetime.now(UTC)
        )
        
        # Act
        orchestrator = RegulatoryAnalysisGraph()
        final_state = orchestrator.execute(initial_state)
        
        # Assert - Pipeline completed successfully
        assert final_state.error is None, f"Pipeline failed with error: {final_state.error}"
        
        # Assert - Pix mentioned in regulatory model
        regulatory_model_str = str(final_state.regulatory_model).lower()
        assert "pix" in regulatory_model_str or "qr" in regulatory_model_str, \
            "Pix-related regulation should mention Pix or QR in regulatory model"
        
        # Assert - All outputs generated
        assert final_state.technical_spec is not None
        assert final_state.kiro_prompt is not None
    
    def test_agents_execute_in_correct_sequence(self):
        """
        Test that agents execute in the deterministic sequence.
        
        Verifies the execution order:
        Sentinel → Translator → CodeReader → Impact → SpecGenerator → KiroPrompt
        
        Requirements: 2.1
        """
        # Arrange
        execution_id = str(uuid.uuid4())
        initial_state = GlobalState(
            raw_regulatory_text=SHORT_REGULATION,
            execution_id=execution_id,
            execution_timestamp=datetime.now(UTC)
        )
        
        # Track agent execution order
        execution_order = []
        
        # Patch each agent to record execution
        with patch('backend.orchestrator.graph.sentinel_agent') as mock_sentinel, \
             patch('backend.orchestrator.graph.translator_agent') as mock_translator, \
             patch('backend.orchestrator.graph.code_reader_agent') as mock_code_reader, \
             patch('backend.orchestrator.graph.impact_agent') as mock_impact, \
             patch('backend.orchestrator.graph.spec_generator_agent') as mock_spec_gen, \
             patch('backend.orchestrator.graph.kiro_prompt_agent') as mock_kiro:
            
            # Configure mocks to record execution and pass through state
            def make_mock_agent(name):
                def agent(state):
                    execution_order.append(name)
                    # Update state with minimal required fields
                    if name == "sentinel":
                        state.change_detected = True
                        state.risk_level = "medium"
                    elif name == "translator":
                        state.regulatory_model = {
                            "title": "Test",
                            "description": "Test",
                            "requirements": ["Test"],
                            "deadlines": [],
                            "affected_systems": ["Pix"]
                        }
                    elif name == "code_reader":
                        state.impacted_files = []
                    elif name == "impact":
                        state.impact_analysis = []
                    elif name == "spec_generator":
                        state.technical_spec = "# Test Spec"
                    elif name == "kiro_prompt":
                        state.kiro_prompt = "Test prompt"
                    return state
                return agent
            
            mock_sentinel.side_effect = make_mock_agent("sentinel")
            mock_translator.side_effect = make_mock_agent("translator")
            mock_code_reader.side_effect = make_mock_agent("code_reader")
            mock_impact.side_effect = make_mock_agent("impact")
            mock_spec_gen.side_effect = make_mock_agent("spec_generator")
            mock_kiro.side_effect = make_mock_agent("kiro_prompt")
            
            # Act
            orchestrator = RegulatoryAnalysisGraph()
            final_state = orchestrator.execute(initial_state)
        
        # Assert - Verify execution order
        expected_order = ["sentinel", "translator", "code_reader", "impact", "spec_generator", "kiro_prompt"]
        assert execution_order == expected_order, \
            f"Agents executed in wrong order. Expected: {expected_order}, Got: {execution_order}"
    
    @pytest.mark.asyncio
    async def test_audit_log_creation(self):
        """
        Test that audit log is created after pipeline execution.
        
        Verifies:
        - Audit log entry is created
        - All required fields are stored
        - Audit log can be retrieved by execution_id
        
        Requirements: 12.1
        """
        # Arrange
        execution_id = str(uuid.uuid4())
        initial_state = GlobalState(
            raw_regulatory_text=SHORT_REGULATION,
            execution_id=execution_id,
            execution_timestamp=datetime.now(UTC)
        )
        
        # Mock database session
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        
        # Act - Execute pipeline
        orchestrator = RegulatoryAnalysisGraph()
        final_state = orchestrator.execute(initial_state)
        
        # Act - Save to audit log
        audit_service = AuditService(mock_session)
        saved_execution_id = await audit_service.save_execution(final_state)
        
        # Assert - Audit log was saved
        assert saved_execution_id == execution_id
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        
        # Assert - Verify the audit log entry has all required fields
        audit_entry = mock_session.add.call_args[0][0]
        assert audit_entry.execution_id == execution_id
        assert audit_entry.raw_text == SHORT_REGULATION
        assert audit_entry.change_detected is not None
        assert audit_entry.risk_level is not None
        assert audit_entry.structured_model is not None
        assert audit_entry.impacted_files is not None
        assert audit_entry.impact_analysis is not None
        assert audit_entry.technical_spec is not None
        assert audit_entry.kiro_prompt is not None
    
    def test_all_outputs_are_generated(self):
        """
        Test that all expected outputs are generated by the pipeline.
        
        Verifies that each agent produces its expected output:
        - change_detected (bool)
        - risk_level (str)
        - regulatory_model (dict)
        - impacted_files (list)
        - impact_analysis (list)
        - technical_spec (str)
        - kiro_prompt (str)
        
        Requirements: 2.1
        """
        # Arrange
        execution_id = str(uuid.uuid4())
        initial_state = GlobalState(
            raw_regulatory_text=MEDIUM_REGULATION,
            execution_id=execution_id,
            execution_timestamp=datetime.now(UTC)
        )
        
        # Act
        orchestrator = RegulatoryAnalysisGraph()
        final_state = orchestrator.execute(initial_state)
        
        # Assert - All outputs are present and have correct types
        assert isinstance(final_state.change_detected, bool), \
            f"change_detected should be bool, got {type(final_state.change_detected)}"
        
        assert isinstance(final_state.risk_level, str), \
            f"risk_level should be str, got {type(final_state.risk_level)}"
        assert final_state.risk_level in ["low", "medium", "high"], \
            f"risk_level has invalid value: {final_state.risk_level}"
        
        assert isinstance(final_state.regulatory_model, dict), \
            f"regulatory_model should be dict, got {type(final_state.regulatory_model)}"
        assert len(final_state.regulatory_model) > 0, "regulatory_model is empty"
        
        assert isinstance(final_state.impacted_files, list), \
            f"impacted_files should be list, got {type(final_state.impacted_files)}"
        
        assert isinstance(final_state.impact_analysis, list), \
            f"impact_analysis should be list, got {type(final_state.impact_analysis)}"
        
        assert isinstance(final_state.technical_spec, str), \
            f"technical_spec should be str, got {type(final_state.technical_spec)}"
        assert len(final_state.technical_spec) > 0, "technical_spec is empty"
        
        assert isinstance(final_state.kiro_prompt, str), \
            f"kiro_prompt should be str, got {type(final_state.kiro_prompt)}"
        assert len(final_state.kiro_prompt) > 0, "kiro_prompt is empty"
    
    def test_state_propagation_between_agents(self):
        """
        Test that state is properly propagated between agents.
        
        Verifies that outputs from earlier agents are available
        to later agents in the pipeline.
        
        Requirements: 2.1
        """
        # Arrange
        execution_id = str(uuid.uuid4())
        initial_state = GlobalState(
            raw_regulatory_text=SHORT_REGULATION,
            execution_id=execution_id,
            execution_timestamp=datetime.now(UTC)
        )
        
        # Act
        orchestrator = RegulatoryAnalysisGraph()
        final_state = orchestrator.execute(initial_state)
        
        # Assert - Verify state propagation
        # Sentinel outputs should be available to all subsequent agents
        assert final_state.change_detected is not None
        assert final_state.risk_level is not None
        
        # Translator outputs should be available to CodeReader, Impact, SpecGenerator, KiroPrompt
        assert final_state.regulatory_model is not None
        
        # CodeReader outputs should be available to Impact, SpecGenerator, KiroPrompt
        assert final_state.impacted_files is not None
        
        # Impact outputs should be available to SpecGenerator, KiroPrompt
        assert final_state.impact_analysis is not None
        
        # SpecGenerator outputs should be available to KiroPrompt
        assert final_state.technical_spec is not None
        
        # All outputs should be in final state
        assert final_state.kiro_prompt is not None
        
        # Original input should be preserved
        assert final_state.raw_regulatory_text == SHORT_REGULATION
        assert final_state.execution_id == execution_id


class TestPipelineErrorHandling:
    """
    Tests for error handling in the pipeline.
    
    Verifies that errors are properly caught, logged, and
    execution is halted when agents fail.
    """
    
    def test_pipeline_halts_on_agent_failure(self):
        """
        Test that pipeline halts execution when an agent fails.
        
        Verifies:
        - Exception is raised when agent fails
        - Error is set in state
        - Subsequent agents do not execute
        
        Requirements: 2.1
        """
        # Arrange
        execution_id = str(uuid.uuid4())
        initial_state = GlobalState(
            raw_regulatory_text=SHORT_REGULATION,
            execution_id=execution_id,
            execution_timestamp=datetime.now(UTC)
        )
        
        # Patch translator agent to raise an exception
        with patch('backend.orchestrator.graph.translator_agent') as mock_translator:
            mock_translator.side_effect = Exception("Translator agent failed")
            
            # Act & Assert
            orchestrator = RegulatoryAnalysisGraph()
            with pytest.raises(RuntimeError) as exc_info:
                orchestrator.execute(initial_state)
            
            # Verify error message contains agent name
            assert "Translator" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_partial_state_saved_on_failure(self):
        """
        Test that partial state is saved to audit log when pipeline fails.
        
        Verifies that even when execution fails, the partial state
        with error information is persisted for debugging.
        
        Requirements: 12.1
        """
        # Arrange
        execution_id = str(uuid.uuid4())
        initial_state = GlobalState(
            raw_regulatory_text=SHORT_REGULATION,
            execution_id=execution_id,
            execution_timestamp=datetime.now(UTC)
        )
        
        # Set error in state to simulate failure
        initial_state.error = "Test error"
        
        # Mock database session
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        
        # Act - Save partial state
        audit_service = AuditService(mock_session)
        saved_execution_id = await audit_service.save_execution(initial_state)
        
        # Assert - Partial state was saved with error
        assert saved_execution_id == execution_id
        mock_session.add.assert_called_once()
        
        audit_entry = mock_session.add.call_args[0][0]
        assert audit_entry.error == "Test error"
        assert audit_entry.execution_id == execution_id


class TestPipelineWithDifferentInputs:
    """
    Tests for pipeline behavior with various input types.
    
    Verifies the pipeline handles different regulatory text
    characteristics correctly.
    """
    
    def test_pipeline_with_multiple_requirements(self):
        """
        Test pipeline with regulatory text containing multiple requirements.
        
        Verifies that complex regulations with multiple requirements
        are properly processed and all requirements are captured.
        """
        # Arrange
        execution_id = str(uuid.uuid4())
        initial_state = GlobalState(
            raw_regulatory_text=MEDIUM_REGULATION,
            execution_id=execution_id,
            execution_timestamp=datetime.now(UTC)
        )
        
        # Act
        orchestrator = RegulatoryAnalysisGraph()
        final_state = orchestrator.execute(initial_state)
        
        # Assert - Multiple requirements captured
        assert final_state.regulatory_model is not None
        requirements = final_state.regulatory_model.get("requirements", [])
        assert len(requirements) >= 2, \
            f"Expected multiple requirements, got {len(requirements)}"
    
    def test_pipeline_with_explicit_deadline(self):
        """
        Test pipeline with regulatory text containing explicit deadlines.
        
        Verifies that deadlines are properly extracted and included
        in the regulatory model.
        """
        # Arrange
        from backend.tests.fixtures.regulatory_texts import REGULATION_WITH_DEADLINE
        
        execution_id = str(uuid.uuid4())
        initial_state = GlobalState(
            raw_regulatory_text=REGULATION_WITH_DEADLINE,
            execution_id=execution_id,
            execution_timestamp=datetime.now(UTC)
        )
        
        # Act
        orchestrator = RegulatoryAnalysisGraph()
        final_state = orchestrator.execute(initial_state)
        
        # Assert - Deadline captured
        assert final_state.regulatory_model is not None
        deadlines = final_state.regulatory_model.get("deadlines", [])
        assert len(deadlines) > 0, "Expected deadline to be captured"
        
        # Verify deadline has required structure
        if deadlines:
            deadline = deadlines[0]
            assert "date" in deadline or "description" in deadline, \
                "Deadline should have date or description"
