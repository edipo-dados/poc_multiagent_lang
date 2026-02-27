"""
Unit tests for GraphVisualizer service.

Tests Mermaid diagram generation with various Global State configurations.
"""

import pytest
from datetime import datetime, UTC

from backend.services.graph_visualizer import GraphVisualizer
from backend.models.state import GlobalState


@pytest.fixture
def sample_state():
    """Create a sample GlobalState with all fields populated."""
    return GlobalState(
        raw_regulatory_text="Sample regulatory text about Pix changes",
        change_detected=True,
        risk_level="high",
        regulatory_model={
            "title": "New Pix Regulation 2024",
            "description": "Updates to Pix transaction limits",
            "requirements": ["Increase limit to R$5000", "Add validation"],
            "deadlines": [{"date": "2024-12-31", "description": "Implementation deadline"}],
            "affected_systems": ["Pix"]
        },
        impacted_files=[
            {"file_path": "api/endpoints.py", "relevance_score": 0.95, "snippet": "..."},
            {"file_path": "domain/validators.py", "relevance_score": 0.87, "snippet": "..."}
        ],
        impact_analysis=[
            {
                "file_path": "api/endpoints.py",
                "impact_type": "api_contract",
                "severity": "high",
                "description": "Update transaction limit validation",
                "suggested_changes": ["Modify limit constant"]
            }
        ],
        technical_spec="# Technical Specification\n\n## Overview\n...",
        kiro_prompt="CONTEXT:\nNew Pix regulation...",
        execution_id="test-123",
        execution_timestamp=datetime.now(UTC)
    )


@pytest.fixture
def minimal_state():
    """Create a minimal GlobalState with only required fields."""
    return GlobalState(
        raw_regulatory_text="Minimal text",
        execution_id="test-minimal"
    )


def test_generate_mermaid_diagram_with_full_state(sample_state):
    """Test Mermaid diagram generation with fully populated state."""
    visualizer = GraphVisualizer()
    diagram = visualizer.generate_mermaid_diagram(sample_state)
    
    # Verify diagram is generated
    assert diagram is not None
    assert len(diagram) > 0
    
    # Verify it's valid Mermaid syntax
    assert diagram.startswith("graph LR")
    
    # Verify all six agents are present
    assert "Sentinel Agent" in diagram
    assert "Translator Agent" in diagram
    assert "CodeReader Agent" in diagram
    assert "Impact Agent" in diagram
    assert "SpecGenerator Agent" in diagram
    assert "KiroPrompt Agent" in diagram
    
    # Verify execution flow edges
    assert "Start([Input Text]) --> Sentinel" in diagram
    assert "Sentinel --> Translator" in diagram
    assert "Translator --> CodeReader" in diagram
    assert "CodeReader --> Impact" in diagram
    assert "Impact --> SpecGen" in diagram
    assert "SpecGen --> KiroPrompt" in diagram
    assert "KiroPrompt --> End([Complete])" in diagram
    
    # Verify annotations from state
    assert "Change: Yes" in diagram
    assert "Risk: High" in diagram
    assert "2 Files Found" in diagram
    assert "1 Impacts Identified" in diagram


def test_generate_mermaid_diagram_with_minimal_state(minimal_state):
    """Test Mermaid diagram generation with minimal state."""
    visualizer = GraphVisualizer()
    diagram = visualizer.generate_mermaid_diagram(minimal_state)
    
    # Verify diagram is generated even with minimal data
    assert diagram is not None
    assert len(diagram) > 0
    
    # Verify all agents are still present
    assert "Sentinel Agent" in diagram
    assert "Translator Agent" in diagram
    assert "CodeReader Agent" in diagram
    assert "Impact Agent" in diagram
    assert "SpecGenerator Agent" in diagram
    assert "KiroPrompt Agent" in diagram
    
    # Verify default annotations
    assert "Change: Unknown" in diagram or "Change: No" in diagram
    assert "0 Files Found" in diagram
    assert "0 Impacts Identified" in diagram


def test_sentinel_annotation_formats():
    """Test Sentinel agent annotation formatting."""
    visualizer = GraphVisualizer()
    
    # Test with change detected
    state = GlobalState(
        raw_regulatory_text="test",
        change_detected=True,
        risk_level="medium"
    )
    annotation = visualizer._format_sentinel_annotation(state)
    assert "Change: Yes" in annotation
    assert "Risk: Medium" in annotation
    
    # Test with no change detected
    state.change_detected = False
    state.risk_level = "low"
    annotation = visualizer._format_sentinel_annotation(state)
    assert "Change: No" in annotation
    assert "Risk: Low" in annotation
    
    # Test with None values
    state.change_detected = None
    state.risk_level = None
    annotation = visualizer._format_sentinel_annotation(state)
    assert "Change: Unknown" in annotation
    assert "Risk: Unknown" in annotation


def test_translator_annotation_formats():
    """Test Translator agent annotation formatting."""
    visualizer = GraphVisualizer()
    
    # Test with regulatory model
    state = GlobalState(
        raw_regulatory_text="test",
        regulatory_model={"title": "Short Title"}
    )
    annotation = visualizer._format_translator_annotation(state)
    assert "Model: Short Title" in annotation
    
    # Test with long title (should truncate)
    state.regulatory_model = {"title": "This is a very long regulatory title that should be truncated"}
    annotation = visualizer._format_translator_annotation(state)
    assert "..." in annotation
    assert len(annotation) < 50  # Should be truncated
    
    # Test with no model
    state.regulatory_model = None
    annotation = visualizer._format_translator_annotation(state)
    assert "Model Created" in annotation


def test_code_reader_annotation_formats():
    """Test CodeReader agent annotation formatting."""
    visualizer = GraphVisualizer()
    
    # Test with multiple files
    state = GlobalState(
        raw_regulatory_text="test",
        impacted_files=[
            {"file_path": "file1.py", "relevance_score": 0.9, "snippet": "..."},
            {"file_path": "file2.py", "relevance_score": 0.8, "snippet": "..."},
            {"file_path": "file3.py", "relevance_score": 0.7, "snippet": "..."}
        ]
    )
    annotation = visualizer._format_code_reader_annotation(state)
    assert "3 Files Found" in annotation
    
    # Test with no files
    state.impacted_files = []
    annotation = visualizer._format_code_reader_annotation(state)
    assert "0 Files Found" in annotation


def test_impact_annotation_formats():
    """Test Impact agent annotation formatting."""
    visualizer = GraphVisualizer()
    
    # Test with multiple impacts
    state = GlobalState(
        raw_regulatory_text="test",
        impact_analysis=[
            {"file_path": "file1.py", "impact_type": "validation", "severity": "high"},
            {"file_path": "file2.py", "impact_type": "business_logic", "severity": "medium"}
        ]
    )
    annotation = visualizer._format_impact_annotation(state)
    assert "2 Impacts Identified" in annotation
    
    # Test with no impacts
    state.impact_analysis = []
    annotation = visualizer._format_impact_annotation(state)
    assert "0 Impacts Identified" in annotation


def test_export_png_graceful_failure():
    """Test that export_png returns None gracefully when mmdc is not available."""
    visualizer = GraphVisualizer()
    state = GlobalState(raw_regulatory_text="test")
    diagram = visualizer.generate_mermaid_diagram(state)
    
    # Should return None if mmdc not available, not raise exception
    result = visualizer.export_png(diagram)
    assert result is None or isinstance(result, bytes)


def test_mermaid_diagram_structure():
    """Test that generated Mermaid diagram has correct structure."""
    visualizer = GraphVisualizer()
    state = GlobalState(
        raw_regulatory_text="test",
        change_detected=True,
        risk_level="high"
    )
    diagram = visualizer.generate_mermaid_diagram(state)
    
    # Count nodes (should have 8: Start, 6 agents, End)
    node_count = diagram.count("[")
    assert node_count == 8
    
    # Count edges (should have 7 arrows)
    edge_count = diagram.count("-->")
    assert edge_count == 7
    
    # Verify line breaks for annotations
    assert "<br/>" in diagram
