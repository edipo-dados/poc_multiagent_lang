"""
Graph visualization service for multi-agent execution flow.

Generates Mermaid diagrams showing agent execution sequence with
annotations from Global State outputs.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from backend.models.state import GlobalState


class GraphVisualizer:
    """
    Generates visual representations of agent execution flow.
    
    Creates Mermaid diagrams showing the six agents (Sentinel, Translator,
    CodeReader, Impact, SpecGenerator, KiroPrompt) with directed edges
    representing execution order and annotations from Global State.
    """
    
    def generate_mermaid_diagram(self, state: GlobalState) -> str:
        """
        Generate Mermaid diagram showing agent execution flow.
        
        Creates a left-to-right flowchart with nodes for each agent,
        annotated with key outputs from the Global State, and directed
        edges showing the deterministic execution sequence.
        
        Args:
            state: GlobalState containing execution results
            
        Returns:
            Mermaid diagram syntax as string
            
        Requirements: 10.1, 10.2, 10.3
        """
        # Build agent nodes with annotations from state
        sentinel_annotation = self._format_sentinel_annotation(state)
        translator_annotation = self._format_translator_annotation(state)
        code_reader_annotation = self._format_code_reader_annotation(state)
        impact_annotation = self._format_impact_annotation(state)
        spec_gen_annotation = "Spec Created"
        kiro_prompt_annotation = "Prompt Generated"
        
        # Build Mermaid diagram
        diagram = f"""graph LR
    Start([Input Text]) --> Sentinel[Sentinel Agent<br/>{sentinel_annotation}]
    Sentinel --> Translator[Translator Agent<br/>{translator_annotation}]
    Translator --> CodeReader[CodeReader Agent<br/>{code_reader_annotation}]
    CodeReader --> Impact[Impact Agent<br/>{impact_annotation}]
    Impact --> SpecGen[SpecGenerator Agent<br/>{spec_gen_annotation}]
    SpecGen --> KiroPrompt[KiroPrompt Agent<br/>{kiro_prompt_annotation}]
    KiroPrompt --> End([Complete])"""
        
        return diagram
    
    def _format_sentinel_annotation(self, state: GlobalState) -> str:
        """Format Sentinel agent annotation from state."""
        change = "Yes" if state.change_detected else "No" if state.change_detected is not None else "Unknown"
        risk = state.risk_level.capitalize() if state.risk_level else "Unknown"
        return f"Change: {change}<br/>Risk: {risk}"
    
    def _format_translator_annotation(self, state: GlobalState) -> str:
        """Format Translator agent annotation from state."""
        if state.regulatory_model:
            title = state.regulatory_model.get("title", "Untitled")
            # Truncate long titles
            if len(title) > 30:
                title = title[:27] + "..."
            return f"Model: {title}"
        return "Model Created"
    
    def _format_code_reader_annotation(self, state: GlobalState) -> str:
        """Format CodeReader agent annotation from state."""
        n_files = len(state.impacted_files)
        return f"{n_files} Files Found"
    
    def _format_impact_annotation(self, state: GlobalState) -> str:
        """Format Impact agent annotation from state."""
        n_impacts = len(state.impact_analysis)
        return f"{n_impacts} Impacts Identified"
    
    def export_png(self, mermaid_str: str, output_path: Optional[str] = None) -> Optional[bytes]:
        """
        Export Mermaid diagram as PNG using Graphviz if available.
        
        This method attempts to convert the Mermaid diagram to PNG format
        using the mmdc (mermaid-cli) command-line tool. If the tool is not
        available, the method returns None gracefully.
        
        Args:
            mermaid_str: Mermaid diagram syntax string
            output_path: Optional path to save PNG file. If None, returns bytes.
            
        Returns:
            PNG image as bytes if output_path is None and conversion succeeds,
            otherwise None. Returns None if mmdc is not available.
            
        Requirements: 10.5
        """
        try:
            # Check if mmdc (mermaid-cli) is available
            result = subprocess.run(
                ["mmdc", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                return None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # mmdc not available
            return None
        
        # Create temporary file for Mermaid input
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            f.write(mermaid_str)
            input_file = f.name
        
        try:
            # Determine output file
            if output_path:
                output_file = output_path
            else:
                output_file = tempfile.mktemp(suffix='.png')
            
            # Convert Mermaid to PNG using mmdc
            result = subprocess.run(
                ["mmdc", "-i", input_file, "-o", output_file],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            # Read PNG bytes if no output path specified
            if not output_path:
                with open(output_file, 'rb') as f:
                    png_bytes = f.read()
                Path(output_file).unlink()  # Clean up temp file
                return png_bytes
            
            return None  # Success, file saved to output_path
            
        except (subprocess.TimeoutExpired, Exception):
            return None
        finally:
            # Clean up input file
            Path(input_file).unlink(missing_ok=True)
