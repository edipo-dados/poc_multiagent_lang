"""
Global State data model for multi-agent pipeline.

The GlobalState is the central data structure passed between all agents,
containing all inputs, intermediate results, and final outputs.
"""

from datetime import datetime, UTC
from typing import Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class GlobalState(BaseModel):
    """
    Shared state object passed through the agent pipeline.
    
    Each agent reads from and writes to this state, enabling
    deterministic data flow through the multi-agent system.
    
    Requirements: 15.1, 15.2, 15.4
    """
    
    # Input
    raw_regulatory_text: str = Field(
        description="Original regulatory text input from user"
    )
    
    # Sentinel Agent outputs
    change_detected: Optional[bool] = Field(
        default=None,
        description="Whether regulatory changes were detected (True/False)"
    )
    risk_level: Optional[str] = Field(
        default=None,
        description="Risk assessment level: 'low', 'medium', or 'high'"
    )
    
    # Translator Agent outputs
    regulatory_model: Optional[dict] = Field(
        default=None,
        description="Structured regulatory model with title, description, requirements, deadlines, affected_systems"
    )
    
    # CodeReader Agent outputs
    impacted_files: list[dict] = Field(
        default_factory=list,
        description="List of relevant code files with file_path, relevance_score, snippet"
    )
    
    # Impact Agent outputs
    impact_analysis: list[dict] = Field(
        default_factory=list,
        description="Detailed impact analysis with file_path, impact_type, severity, description, suggested_changes"
    )
    
    # SpecGenerator Agent outputs
    technical_spec: Optional[str] = Field(
        default=None,
        description="Markdown technical specification document"
    )
    
    # KiroPrompt Agent outputs
    kiro_prompt: Optional[str] = Field(
        default=None,
        description="Development prompt with instructions for implementation"
    )
    
    # Metadata
    execution_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when execution started"
    )
    execution_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for this execution (UUID)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if execution failed at any agent"
    )
    
    model_config = ConfigDict(
        arbitrary_types_allowed=False
    )
    
    @field_serializer('execution_timestamp')
    def serialize_timestamp(self, dt: datetime, _info):
        """Serialize datetime to ISO format string."""
        return dt.isoformat()
