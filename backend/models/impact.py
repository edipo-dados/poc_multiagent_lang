"""
Impact Analysis data structures.

Models for representing code files and their technical impacts
from regulatory changes.
"""

from typing import Literal
from pydantic import BaseModel, Field


class ImpactedFile(BaseModel):
    """
    Code file identified as relevant by CodeReader Agent.
    
    Represents a file from the repository that may be affected
    by the regulatory change, with a relevance score from semantic search.
    
    Requirements: 5.3
    """
    
    file_path: str = Field(
        description="Relative path to file in repository"
    )
    
    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Cosine similarity score indicating relevance (0.0 to 1.0)"
    )
    
    snippet: str = Field(
        description="First 200 characters of file content for preview"
    )


class Impact(BaseModel):
    """
    Technical impact analysis for a specific file.
    
    Detailed analysis of how a regulatory change affects a particular
    code file, including impact type, severity, and suggested changes.
    
    Requirements: 6.2
    """
    
    file_path: str = Field(
        description="Path to the impacted file"
    )
    
    impact_type: Literal["schema_change", "business_logic", "validation", "api_contract"] = Field(
        description="Category of impact: schema_change (DB models), business_logic (services), validation (rules), api_contract (endpoints)"
    )
    
    severity: Literal["low", "medium", "high"] = Field(
        description="Severity level of the impact"
    )
    
    description: str = Field(
        description="Detailed explanation of the impact and why changes are needed"
    )
    
    suggested_changes: list[str] = Field(
        description="List of recommended code modifications to address the impact"
    )
