"""
Impact Agent - Technical Impact Analysis

The Impact Agent analyzes code files identified by the CodeReader Agent to determine
technical impacts from regulatory changes. It classifies impact types, assesses severity,
and generates suggested changes for each affected file.

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

import logging
import os
from pathlib import Path
from backend.models.state import GlobalState
from backend.models.impact import Impact
from backend.services.llm import get_llm


logger = logging.getLogger(__name__)


def impact_agent(state: GlobalState) -> GlobalState:
    """
    Analyze technical impacts for each identified code file.
    
    This agent performs the fourth step in the multi-agent pipeline:
    1. For each file in impacted_files, load the file content
    2. Analyze the file against regulatory_model using LLM
    3. Classify impact_type based on file path and content
    4. Assess severity (low, medium, high) based on scope and complexity
    5. Generate description explaining why changes are needed
    6. Generate suggested_changes as a list of specific modifications
    7. Update Global State with impact_analysis list
    
    Args:
        state: GlobalState containing regulatory_model and impacted_files
        
    Returns:
        Updated GlobalState with impact_analysis populated
        
    Raises:
        Exception: If file loading fails or LLM analysis encounters errors
        
    Requirements:
        - 6.1: Analyze each file in impacted_files against regulatory_model
        - 6.2: Generate impact_analysis with required fields
        - 6.3: Classify impact_type correctly
        - 6.4: Assign appropriate severity
        - 6.5: Update Global State with complete impact_analysis
    """
    logger.info(f"Impact Agent starting analysis for execution {state.execution_id}")
    
    try:
        # Validate prerequisites
        if not state.regulatory_model:
            raise ValueError("regulatory_model is required but not set")
        
        if not state.impacted_files:
            logger.warning("No impacted files to analyze - returning empty impact_analysis")
            state.impact_analysis = []
            return state
        
        # Get LLM provider
        llm = get_llm()
        
        # Get repository path from environment or use default
        repo_path = os.getenv("PIX_REPO_PATH", "fake_pix_repo")
        
        # Analyze each impacted file
        impact_analysis = []
        for file_info in state.impacted_files:
            try:
                file_path = file_info.get("file_path", "")
                if not file_path:
                    logger.warning(f"Skipping file with empty path: {file_info}")
                    continue
                
                logger.info(f"Analyzing impact for file: {file_path}")
                
                # Load file content
                content = _load_file_content(repo_path, file_path)
                
                # Analyze impact
                impact = _analyze_file_impact(
                    file_path=file_path,
                    content=content,
                    regulatory_model=state.regulatory_model,
                    llm=llm
                )
                
                # Add to analysis list
                impact_analysis.append(impact.model_dump())
                logger.info(f"Impact analysis completed for {file_path}: {impact.impact_type}, {impact.severity}")
                
            except Exception as e:
                logger.error(f"Failed to analyze file {file_info.get('file_path', 'unknown')}: {e}")
                # Continue with other files even if one fails
                continue
        
        # Update state with impact analysis
        state.impact_analysis = impact_analysis
        
        logger.info(f"Impact Agent completed successfully. Analyzed {len(impact_analysis)} files")
        return state
        
    except Exception as e:
        logger.error(f"Impact Agent failed: {str(e)}", exc_info=True)
        state.error = f"Impact Agent error: {str(e)}"
        raise


def _load_file_content(repo_path: str, file_path: str) -> str:
    """
    Load content from a file in the Pix repository.
    
    Args:
        repo_path: Base path to the Pix repository
        file_path: Relative path to the file within the repository
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file does not exist
        IOError: If file cannot be read
    """
    full_path = Path(repo_path) / file_path
    
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {full_path}")
    
    if not full_path.is_file():
        raise IOError(f"Path is not a file: {full_path}")
    
    try:
        content = full_path.read_text(encoding='utf-8')
        logger.debug(f"Loaded {len(content)} characters from {file_path}")
        return content
    except Exception as e:
        raise IOError(f"Failed to read file {full_path}: {e}")


def _classify_impact_type(file_path: str, content: str) -> str:
    """
    Classify the impact type based on file path and content.
    
    Classification rules:
    - schema_change: database/models.py files (SQLAlchemy models)
    - business_logic: services/ and domain/ files (business logic)
    - validation: validators.py files (business rule validators)
    - api_contract: api/endpoints.py and api/schemas.py files (API layer)
    
    Args:
        file_path: Relative path to the file
        content: File content
        
    Returns:
        Impact type: "schema_change", "business_logic", "validation", or "api_contract"
    """
    file_path_lower = file_path.lower()
    
    # Check for database models (schema changes)
    if "database" in file_path_lower and "models.py" in file_path_lower:
        return "schema_change"
    
    # Check for validators
    if "validators.py" in file_path_lower or "validator" in file_path_lower:
        return "validation"
    
    # Check for API endpoints and schemas
    if "api" in file_path_lower:
        if "endpoints.py" in file_path_lower or "schemas.py" in file_path_lower:
            return "api_contract"
    
    # Check for services and domain logic
    if "services" in file_path_lower or "domain" in file_path_lower:
        return "business_logic"
    
    # Default to business_logic for other files
    logger.debug(f"Defaulting to business_logic for {file_path}")
    return "business_logic"


def _analyze_file_impact(
    file_path: str,
    content: str,
    regulatory_model: dict,
    llm
) -> Impact:
    """
    Analyze the impact of regulatory changes on a specific file.
    
    Uses LLM to understand how the regulatory requirements affect the code
    and generates specific recommendations for changes.
    
    Args:
        file_path: Path to the file being analyzed
        content: File content
        regulatory_model: Structured regulatory model
        llm: LLM provider instance
        
    Returns:
        Impact object with analysis results
    """
    # Classify impact type based on file path and content
    impact_type = _classify_impact_type(file_path, content)
    
    # Build context for LLM analysis
    requirements_text = "\n".join(f"- {req}" for req in regulatory_model.get("requirements", []))
    affected_systems = ", ".join(regulatory_model.get("affected_systems", []))
    
    # Create analysis prompt
    prompt = f"""Analise o impacto de uma mudança regulatória em um arquivo de código.

MUDANÇA REGULATÓRIA:
Título: {regulatory_model.get('title', 'N/A')}
Descrição: {regulatory_model.get('description', 'N/A')}

Requisitos:
{requirements_text}

Sistemas Afetados: {affected_systems}

ARQUIVO A ANALISAR:
Caminho: {file_path}
Tipo de Impacto: {impact_type}

Conteúdo (primeiros 1500 caracteres):
{content[:1500]}

TAREFA:
1. Avalie a SEVERIDADE do impacto (LOW, MEDIUM, HIGH):
   - HIGH: Mudanças obrigatórias complexas, múltiplas alterações necessárias
   - MEDIUM: Mudanças moderadas, algumas alterações necessárias
   - LOW: Mudanças simples ou mínimas

2. Descreva o IMPACTO: Por que este arquivo precisa ser modificado?

3. Liste MUDANÇAS SUGERIDAS: Modificações específicas necessárias (3-5 itens)

Responda no formato:
SEVERIDADE: [LOW/MEDIUM/HIGH]
DESCRIÇÃO: [explicação do impacto]
MUDANÇAS:
- [mudança 1]
- [mudança 2]
- [mudança 3]

Resposta:"""

    try:
        # Generate analysis from LLM
        response = llm.generate(prompt, max_tokens=1500)
        logger.debug(f"LLM impact analysis response (first 200 chars): {response[:200]}")
        
        # Parse LLM response
        severity, description, suggested_changes = _parse_impact_response(response)
        
        # Create Impact object
        impact = Impact(
            file_path=file_path,
            impact_type=impact_type,
            severity=severity,
            description=description,
            suggested_changes=suggested_changes
        )
        
        return impact
        
    except Exception as e:
        logger.error(f"LLM analysis failed for {file_path}: {e}")
        # Return fallback impact analysis
        return _create_fallback_impact(file_path, impact_type, regulatory_model)


def _parse_impact_response(response: str) -> tuple[str, str, list[str]]:
    """
    Parse LLM response to extract severity, description, and suggested changes.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        Tuple of (severity, description, suggested_changes)
    """
    # Default values
    severity = "medium"
    description = "Impact analysis pending"
    suggested_changes = []
    
    lines = response.strip().split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        # Parse severity
        if line.upper().startswith("SEVERIDADE:") or line.upper().startswith("SEVERITY:"):
            severity_text = line.split(':', 1)[1].strip().upper()
            if "HIGH" in severity_text or "ALTO" in severity_text or "ALTA" in severity_text:
                severity = "high"
            elif "MEDIUM" in severity_text or "MÉDIO" in severity_text or "MEDIA" in severity_text:
                severity = "medium"
            elif "LOW" in severity_text or "BAIXO" in severity_text or "BAIXA" in severity_text:
                severity = "low"
        
        # Parse description
        elif line.upper().startswith("DESCRIÇÃO:") or line.upper().startswith("DESCRIPTION:") or line.upper().startswith("IMPACTO:"):
            description = line.split(':', 1)[1].strip()
            current_section = "description"
        
        # Parse changes section
        elif line.upper().startswith("MUDANÇAS:") or line.upper().startswith("CHANGES:") or line.upper().startswith("SUGESTÕES:"):
            current_section = "changes"
        
        # Collect change items
        elif current_section == "changes" and line.startswith('-'):
            change = line.lstrip('- ').strip()
            if change:
                suggested_changes.append(change)
        
        # Continue description if multi-line
        elif current_section == "description" and line and not line.startswith('-'):
            if not any(keyword in line.upper() for keyword in ["MUDANÇAS:", "CHANGES:", "SEVERIDADE:", "SEVERITY:"]):
                description += " " + line
    
    # Ensure we have at least one suggested change
    if not suggested_changes:
        suggested_changes = ["Review and update code to comply with regulatory requirements"]
    
    # Clean up description
    description = description.strip()
    if not description or description == "Impact analysis pending":
        description = f"This file requires modifications to comply with the regulatory changes."
    
    logger.debug(f"Parsed impact: severity={severity}, changes_count={len(suggested_changes)}")
    return severity, description, suggested_changes


def _create_fallback_impact(file_path: str, impact_type: str, regulatory_model: dict) -> Impact:
    """
    Create a fallback impact analysis when LLM fails.
    
    Args:
        file_path: Path to the file
        impact_type: Classified impact type
        regulatory_model: Regulatory model for context
        
    Returns:
        Fallback Impact object
    """
    # Generate generic description based on impact type
    impact_descriptions = {
        "schema_change": "Database schema modifications may be required to support new regulatory requirements.",
        "business_logic": "Business logic updates needed to implement regulatory compliance rules.",
        "validation": "Validation rules must be updated to enforce new regulatory constraints.",
        "api_contract": "API contracts may need modifications to support regulatory data requirements."
    }
    
    description = impact_descriptions.get(impact_type, "Code modifications required for regulatory compliance.")
    
    # Generate generic suggested changes
    suggested_changes = [
        f"Review {file_path} against regulatory requirements",
        "Update code to implement required compliance rules",
        "Add or modify validation logic as needed",
        "Update tests to cover new regulatory scenarios"
    ]
    
    impact = Impact(
        file_path=file_path,
        impact_type=impact_type,
        severity="medium",
        description=description,
        suggested_changes=suggested_changes
    )
    
    logger.info(f"Created fallback impact for {file_path}")
    return impact
