"""
Translator Agent - Regulatory Text Structuring

The Translator Agent structures regulatory text into a formal RegulatoryModel.
It extracts structured fields (title, description, requirements, deadlines, 
affected_systems) using an LLM and validates the JSON structure.

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
"""

import logging
import json
from typing import Optional
from backend.models.state import GlobalState
from backend.models.regulatory import RegulatoryModel
from backend.services.llm import get_llm


logger = logging.getLogger(__name__)


def translator_agent(state: GlobalState) -> GlobalState:
    """
    Extract structured information from regulatory text.
    
    This agent performs the second step in the multi-agent pipeline:
    1. Uses LLM to extract structured fields from raw text
    2. Identifies requirements as actionable items
    3. Parses dates and associates with requirement descriptions
    4. Identifies affected system names
    5. Validates JSON structure
    6. Updates Global State with regulatory_model
    
    Args:
        state: GlobalState containing raw_regulatory_text
        
    Returns:
        Updated GlobalState with regulatory_model set
        
    Raises:
        Exception: If LLM generation fails or JSON validation fails
        
    Requirements:
        - 4.1: Extract structured information from raw_regulatory_text
        - 4.2: Create regulatory_model with required fields
        - 4.3: Update Global State with regulatory_model
        - 4.4: Format as valid JSON
        - 4.5: Ensure round-trip serialization
    """
    logger.info(f"Translator Agent starting for execution {state.execution_id}")
    
    try:
        # Get LLM provider
        llm = get_llm()
        
        # Extract structured information using LLM
        regulatory_model = _extract_structured_data(state.raw_regulatory_text, llm)
        
        # Validate the model (ensures all required fields present)
        _validate_regulatory_model(regulatory_model)
        
        # Convert to dict and update state
        state.regulatory_model = regulatory_model.model_dump()
        
        logger.info(f"Translator Agent completed successfully. Title: {regulatory_model.title}")
        return state
        
    except Exception as e:
        logger.error(f"Translator Agent failed: {str(e)}", exc_info=True)
        state.error = f"Translator Agent error: {str(e)}"
        raise


def _extract_structured_data(text: str, llm) -> RegulatoryModel:
    """
    Extract structured fields from regulatory text using LLM.
    
    Uses a carefully crafted prompt to guide the LLM to extract:
    - title: Brief title of the regulatory change
    - description: Detailed description
    - requirements: List of actionable requirements
    - deadlines: List of dates with descriptions
    - affected_systems: List of system names mentioned
    
    Args:
        text: Raw regulatory text
        llm: LLM provider instance
        
    Returns:
        RegulatoryModel with extracted fields
        
    Raises:
        Exception: If LLM fails or JSON parsing fails
    """
    prompt = f"""Analise o seguinte texto regulatório e extraia informações estruturadas.

Texto Regulatório:
{text}

Extraia as seguintes informações e retorne APENAS um objeto JSON válido (sem texto adicional):

{{
  "title": "Título breve da mudança regulatória",
  "description": "Descrição detalhada do que a regulação estabelece",
  "requirements": ["Requisito 1", "Requisito 2", "..."],
  "deadlines": [{{"date": "YYYY-MM-DD", "description": "Descrição do prazo"}}],
  "affected_systems": ["Sistema 1", "Sistema 2", "..."]
}}

Instruções:
- title: Crie um título conciso (máximo 100 caracteres)
- description: Resuma o propósito e escopo da regulação
- requirements: Liste itens acionáveis específicos (use verbos como "deve", "precisa")
- deadlines: Extraia todas as datas mencionadas no formato YYYY-MM-DD
- affected_systems: Identifique sistemas mencionados (ex: "Pix", "pagamentos", "transferências")

JSON:"""

    try:
        # Generate response from LLM
        response = llm.generate(prompt, max_tokens=2000)
        logger.debug(f"LLM response (first 200 chars): {response[:200]}")
        
        # Parse JSON from response
        json_data = _extract_json_from_response(response)
        
        # Create and validate RegulatoryModel
        model = RegulatoryModel(**json_data)
        
        # Ensure round-trip serialization works (Requirement 4.5)
        _test_round_trip_serialization(model)
        
        return model
        
    except Exception as e:
        logger.error(f"Failed to extract structured data: {e}")
        # If LLM fails, create a minimal valid model
        logger.warning("Creating fallback regulatory model with minimal data")
        return _create_fallback_model(text)


def _extract_json_from_response(response: str) -> dict:
    """
    Extract JSON object from LLM response.
    
    LLMs sometimes include extra text before/after the JSON.
    This function attempts to find and parse the JSON object.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        ValueError: If no valid JSON found
    """
    # Try to parse the entire response first
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON object in response (between { and })
    start_idx = response.find('{')
    end_idx = response.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = response[start_idx:end_idx + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extracted JSON: {e}")
            raise ValueError(f"Could not parse JSON from LLM response: {e}")
    
    raise ValueError("No valid JSON object found in LLM response")


def _validate_regulatory_model(model: RegulatoryModel) -> None:
    """
    Validate that regulatory model has all required fields.
    
    Args:
        model: RegulatoryModel to validate
        
    Raises:
        ValueError: If any required field is missing or invalid
    """
    # Check required string fields are non-empty
    if not model.title or not model.title.strip():
        raise ValueError("Regulatory model must have a non-empty title")
    
    if not model.description or not model.description.strip():
        raise ValueError("Regulatory model must have a non-empty description")
    
    # Check lists are present (can be empty)
    if model.requirements is None:
        raise ValueError("Regulatory model must have requirements list (can be empty)")
    
    if model.deadlines is None:
        raise ValueError("Regulatory model must have deadlines list (can be empty)")
    
    if model.affected_systems is None:
        raise ValueError("Regulatory model must have affected_systems list (can be empty)")
    
    # Validate deadline structure
    for deadline in model.deadlines:
        if not isinstance(deadline, dict):
            raise ValueError(f"Deadline must be a dict, got {type(deadline)}")
        if "date" not in deadline or "description" not in deadline:
            raise ValueError(f"Deadline must have 'date' and 'description' keys: {deadline}")
    
    logger.debug("Regulatory model validation passed")


def _test_round_trip_serialization(model: RegulatoryModel) -> None:
    """
    Test that model can be serialized and deserialized without loss.
    
    This ensures Requirement 4.5: round-trip property.
    
    Args:
        model: RegulatoryModel to test
        
    Raises:
        ValueError: If round-trip serialization fails
    """
    try:
        # Serialize to JSON
        json_str = model.model_dump_json()
        
        # Deserialize back to model
        restored = RegulatoryModel.model_validate_json(json_str)
        
        # Compare
        if model != restored:
            raise ValueError("Round-trip serialization produced different model")
        
        logger.debug("Round-trip serialization test passed")
        
    except Exception as e:
        logger.error(f"Round-trip serialization failed: {e}")
        raise ValueError(f"Model failed round-trip serialization: {e}")


def _create_fallback_model(text: str) -> RegulatoryModel:
    """
    Create a minimal fallback regulatory model when LLM fails.
    
    This ensures the pipeline can continue even if LLM extraction fails.
    
    Args:
        text: Original regulatory text
        
    Returns:
        Minimal valid RegulatoryModel
    """
    # Extract first sentence or first 100 chars as title
    first_line = text.split('\n')[0].strip()
    title = first_line[:100] if first_line else "Regulatory Change"
    
    # Use first 500 chars as description
    description = text[:500].strip() if text else "No description available"
    
    # Try to identify system names with simple keyword matching
    text_lower = text.lower()
    affected_systems = []
    system_keywords = ["pix", "pagamento", "transferência", "ted", "doc"]
    for keyword in system_keywords:
        if keyword in text_lower:
            affected_systems.append(keyword.capitalize())
    
    model = RegulatoryModel(
        title=title,
        description=description,
        requirements=["Manual review required - LLM extraction failed"],
        deadlines=[],
        affected_systems=affected_systems if affected_systems else ["Unknown"]
    )
    
    logger.info(f"Created fallback model with title: {title}")
    return model
