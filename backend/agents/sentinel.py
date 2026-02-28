"""
Sentinel Agent - Change Detection and Risk Assessment

The Sentinel Agent analyzes regulatory text to detect changes and assess risk levels.
It identifies keywords indicating regulatory changes and classifies risk based on
urgency and scope.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import logging
from backend.models.state import GlobalState
from backend.services.llm import get_llm


logger = logging.getLogger(__name__)


# Keywords indicating regulatory changes (Portuguese)
CHANGE_KEYWORDS = [
    "alteração",
    "nova regra",
    "obrigatório",
    "mudança",
    "modificação",
    "atualização",
    "revisão",
    "novo requisito",
    "deve",
    "deverá",
    "é necessário"
]

# Keywords indicating high urgency
HIGH_URGENCY_KEYWORDS = [
    "imediato",
    "urgente",
    "prazo curto",
    "obrigatório",
    "compliance",
    "penalidade",
    "multa",
    "sanção"
]

# Keywords indicating medium urgency
MEDIUM_URGENCY_KEYWORDS = [
    "recomendado",
    "sugerido",
    "prazo moderado",
    "gradual",
    "transição"
]


def sentinel_agent(state: GlobalState) -> GlobalState:
    """
    Analyze regulatory text for changes and assess risk level.
    
    This agent performs the first step in the multi-agent pipeline:
    1. Parses regulatory text using LLM
    2. Detects if changes are present
    3. Classifies risk level (low, medium, high)
    4. Updates Global State with results
    
    Args:
        state: GlobalState containing raw_regulatory_text
        
    Returns:
        Updated GlobalState with change_detected and risk_level set
        
    Raises:
        Exception: If LLM generation fails or processing encounters errors
        
    Requirements:
        - 3.1: Analyze text for regulatory changes
        - 3.2: Set change_detected to true or false
        - 3.3: Determine risk_level (low, medium, high)
        - 3.4: Update Global State with results
        - 3.5: Complete within 10 seconds for texts up to 10,000 characters
    """
    logger.info(f"Sentinel Agent starting analysis for execution {state.execution_id}")
    
    try:
        # Get LLM provider
        llm = get_llm()
        
        # Step 1: Detect changes using LLM
        change_detected = _detect_changes(state.raw_regulatory_text, llm)
        state.change_detected = change_detected
        logger.info(f"Change detection result: {change_detected}")
        
        # Step 2: Assess risk level using LLM
        risk_level = _assess_risk(state.raw_regulatory_text, llm, change_detected)
        state.risk_level = risk_level
        logger.info(f"Risk assessment result: {risk_level}")
        
        logger.info("Sentinel Agent completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"Sentinel Agent failed: {str(e)}", exc_info=True)
        # Set default values to indicate failure
        state.change_detected = False
        state.risk_level = "low"
        state.error = f"Sentinel Agent error: {str(e)}"
        raise


def _detect_changes(text: str, llm) -> bool:
    """
    Detect if regulatory text contains changes.
    
    Uses a combination of keyword matching and LLM analysis to determine
    if the text describes regulatory changes.
    
    Args:
        text: Regulatory text to analyze
        llm: LLM provider instance
        
    Returns:
        True if changes detected, False otherwise
        
    Raises:
        Exception: If LLM fails and no keywords found (critical failure)
    """
    # Quick keyword check first
    text_lower = text.lower()
    keyword_matches = sum(1 for keyword in CHANGE_KEYWORDS if keyword in text_lower)
    
    # If multiple keywords found, likely contains changes
    if keyword_matches >= 2:
        logger.debug(f"Found {keyword_matches} change keywords - likely contains changes")
        has_changes = True
    else:
        # Use LLM for more nuanced analysis
        prompt = f"""Analise o seguinte texto regulatório e determine se ele descreve mudanças ou alterações em regras existentes.

Texto:
{text[:2000]}

Responda apenas com "SIM" se o texto descreve mudanças/alterações, ou "NÃO" se é apenas informativo.
Resposta:"""
        
        try:
            response = llm.generate(prompt, max_tokens=50)
            has_changes = "sim" in response.lower()
            logger.debug(f"LLM change detection response: {response.strip()}")
        except Exception as e:
            logger.warning(f"LLM call failed for change detection: {e}")
            # Fallback to keyword-based detection
            if keyword_matches > 0:
                has_changes = True
            else:
                # No keywords and LLM failed - this is a critical failure
                raise
    
    return has_changes


def _assess_risk(text: str, llm, change_detected: bool) -> str:
    """
    Assess risk level of regulatory text.
    
    Classifies risk based on urgency indicators and scope:
    - High: Mandatory changes with near deadlines, penalties mentioned
    - Medium: Recommended changes or moderate deadlines
    - Low: Informational or distant deadlines, no changes detected
    
    Args:
        text: Regulatory text to analyze
        llm: LLM provider instance
        change_detected: Whether changes were detected
        
    Returns:
        Risk level: "low", "medium", or "high"
    """
    # If no changes detected, risk is low
    if not change_detected:
        logger.debug("No changes detected - risk level: low")
        return "low"
    
    # Check for urgency keywords
    text_lower = text.lower()
    high_urgency_count = sum(1 for keyword in HIGH_URGENCY_KEYWORDS if keyword in text_lower)
    medium_urgency_count = sum(1 for keyword in MEDIUM_URGENCY_KEYWORDS if keyword in text_lower)
    
    # Keyword-based classification
    if high_urgency_count >= 2:
        logger.debug(f"Found {high_urgency_count} high urgency keywords - risk level: high")
        return "high"
    elif high_urgency_count >= 1 or medium_urgency_count >= 1:
        logger.debug(f"Found urgency keywords (high: {high_urgency_count}, medium: {medium_urgency_count}) - risk level: medium")
        return "medium"
    
    # Use LLM for more nuanced risk assessment
    prompt = f"""Analise o seguinte texto regulatório e classifique o nível de risco para implementação.

Texto:
{text[:2000]}

Critérios:
- ALTO: Mudanças obrigatórias com prazos próximos, penalidades mencionadas
- MÉDIO: Mudanças recomendadas ou prazos moderados
- BAIXO: Informativo ou prazos distantes

Responda apenas com: ALTO, MÉDIO ou BAIXO
Resposta:"""
    
    try:
        response = llm.generate(prompt, max_tokens=10)
        response_lower = response.lower().strip()
        
        if "alto" in response_lower or "high" in response_lower:
            risk = "high"
        elif "médio" in response_lower or "medio" in response_lower or "medium" in response_lower:
            risk = "medium"
        else:
            risk = "low"
        
        logger.debug(f"LLM risk assessment response: {response.strip()} -> {risk}")
        return risk
        
    except Exception as e:
        logger.warning(f"LLM call failed for risk assessment: {e}")
        # Fallback to keyword-based assessment
        if high_urgency_count > 0:
            return "medium"
        return "low"
