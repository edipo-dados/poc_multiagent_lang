"""
Regulatory Model data structure.

Structured representation of regulatory text extracted by Translator Agent.
"""

from pydantic import BaseModel, Field


class RegulatoryModel(BaseModel):
    """
    Formal structure of regulatory requirements.
    
    This model represents the structured output from the Translator Agent,
    which extracts key information from unstructured regulatory text.
    
    Requirements: 4.2
    """
    
    title: str = Field(
        description="Regulatory change title or name"
    )
    
    description: str = Field(
        description="Detailed description of the regulation and its purpose"
    )
    
    requirements: list[str] = Field(
        description="List of specific actionable requirements from the regulation"
    )
    
    deadlines: list[dict[str, str]] = Field(
        description="Deadlines with 'date' and 'description' keys",
        examples=[[{"date": "2024-12-31", "description": "Implementation deadline"}]]
    )
    
    affected_systems: list[str] = Field(
        description="Systems or components impacted by this regulation (e.g., 'Pix', 'pagamentos')"
    )
