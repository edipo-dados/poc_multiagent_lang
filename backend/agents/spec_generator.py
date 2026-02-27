"""
SpecGenerator Agent - Technical Specification Generation

The SpecGenerator Agent generates a structured technical specification document
from the impact analysis. It creates a Markdown document with sections for
overview, affected components, required changes, acceptance criteria, and
estimated effort.

Requirements: 7.1, 7.2, 7.3, 7.4
"""

import logging
from backend.models.state import GlobalState
from backend.services.llm import get_llm


logger = logging.getLogger(__name__)


def spec_generator_agent(state: GlobalState) -> GlobalState:
    """
    Generate technical specification document from analysis results.
    
    This agent performs the fifth step in the multi-agent pipeline:
    1. Generate overview from regulatory_model
    2. List all impacted files grouped by impact_type
    3. Detail required changes for each file
    4. Convert regulatory requirements to acceptance criteria
    5. Estimate effort based on severity weights (high=3, medium=2, low=1)
    6. Format as Markdown string
    7. Update Global State with technical_spec
    
    Args:
        state: GlobalState containing regulatory_model and impact_analysis
        
    Returns:
        Updated GlobalState with technical_spec populated
        
    Raises:
        Exception: If specification generation fails
        
    Requirements:
        - 7.1: Generate technical_spec document
        - 7.2: Include required sections (overview, affected_components, 
               required_changes, acceptance_criteria, estimated_effort)
        - 7.3: Reference all files from impact_analysis
        - 7.4: Format as Markdown
    """
    logger.info(f"SpecGenerator Agent starting for execution {state.execution_id}")
    
    try:
        # Validate prerequisites
        if not state.regulatory_model:
            raise ValueError("regulatory_model is required but not set")
        
        if not state.impact_analysis:
            logger.warning("No impact analysis available - generating minimal spec")
            state.technical_spec = _generate_minimal_spec(state.regulatory_model)
            return state
        
        # Get LLM provider
        llm = get_llm()
        
        # Generate technical specification
        technical_spec = _generate_technical_spec(
            regulatory_model=state.regulatory_model,
            impact_analysis=state.impact_analysis,
            llm=llm
        )
        
        # Update state with technical spec
        state.technical_spec = technical_spec
        
        logger.info(f"SpecGenerator Agent completed successfully. Spec length: {len(technical_spec)} chars")
        return state
        
    except Exception as e:
        logger.error(f"SpecGenerator Agent failed: {str(e)}", exc_info=True)
        state.error = f"SpecGenerator Agent error: {str(e)}"
        raise


def _generate_technical_spec(
    regulatory_model: dict,
    impact_analysis: list[dict],
    llm
) -> str:
    """
    Generate complete technical specification document.
    
    Creates a Markdown document with all required sections:
    - Overview: Summary of regulatory change
    - Affected Components: Files grouped by impact type
    - Required Changes: Detailed changes per file
    - Acceptance Criteria: Testable criteria from requirements
    - Estimated Effort: Calculated from severity weights
    
    Args:
        regulatory_model: Structured regulatory model
        impact_analysis: List of impact objects
        llm: LLM provider instance
        
    Returns:
        Complete technical specification as Markdown string
    """
    # Build the specification sections
    title = regulatory_model.get("title", "Technical Specification")
    overview = _generate_overview(regulatory_model, llm)
    affected_components = _generate_affected_components(impact_analysis)
    required_changes = _generate_required_changes(impact_analysis)
    acceptance_criteria = _generate_acceptance_criteria(regulatory_model, llm)
    estimated_effort = _calculate_estimated_effort(impact_analysis)
    
    # Assemble the complete specification
    spec = f"""# Technical Specification: {title}

## Overview

{overview}

## Affected Components

{affected_components}

## Required Changes

{required_changes}

## Acceptance Criteria

{acceptance_criteria}

## Estimated Effort

{estimated_effort}
"""
    
    logger.debug(f"Generated technical spec with {len(spec)} characters")
    return spec


def _generate_overview(regulatory_model: dict, llm) -> str:
    """
    Generate overview section from regulatory model.
    
    Uses the regulatory model description and requirements to create
    a concise overview of the regulatory change and its implications.
    
    Args:
        regulatory_model: Structured regulatory model
        llm: LLM provider instance
        
    Returns:
        Overview text
    """
    description = regulatory_model.get("description", "")
    requirements = regulatory_model.get("requirements", [])
    affected_systems = regulatory_model.get("affected_systems", [])
    deadlines = regulatory_model.get("deadlines", [])
    
    # Build context for LLM
    requirements_text = "\n".join(f"- {req}" for req in requirements)
    systems_text = ", ".join(affected_systems) if affected_systems else "N/A"
    
    deadlines_text = ""
    if deadlines:
        deadlines_text = "\n".join(
            f"- {d.get('date', 'N/A')}: {d.get('description', 'N/A')}" 
            for d in deadlines
        )
    
    prompt = f"""Crie um resumo executivo conciso (2-3 parágrafos) para uma especificação técnica.

MUDANÇA REGULATÓRIA:
{description}

REQUISITOS:
{requirements_text}

SISTEMAS AFETADOS: {systems_text}

PRAZOS:
{deadlines_text if deadlines_text else "Nenhum prazo específico mencionado"}

Escreva um resumo que:
1. Explique o propósito da mudança regulatória
2. Destaque os principais requisitos técnicos
3. Mencione os sistemas impactados e prazos relevantes

Resumo:"""

    try:
        overview = llm.generate(prompt, max_tokens=500)
        return overview.strip()
    except Exception as e:
        logger.error(f"LLM failed to generate overview: {e}")
        # Fallback to simple description
        return f"{description}\n\nSistemas Afetados: {systems_text}"


def _generate_affected_components(impact_analysis: list[dict]) -> str:
    """
    Generate affected components section.
    
    Lists all impacted files grouped by impact_type with severity indicators.
    
    Args:
        impact_analysis: List of impact objects
        
    Returns:
        Markdown formatted list of affected components
    """
    # Group files by impact type
    grouped = {}
    for impact in impact_analysis:
        impact_type = impact.get("impact_type", "unknown")
        if impact_type not in grouped:
            grouped[impact_type] = []
        grouped[impact_type].append(impact)
    
    # Build markdown list
    sections = []
    
    # Define display names for impact types
    type_names = {
        "schema_change": "Database Schema Changes",
        "business_logic": "Business Logic",
        "validation": "Validation Rules",
        "api_contract": "API Contracts"
    }
    
    for impact_type, impacts in grouped.items():
        type_name = type_names.get(impact_type, impact_type.replace("_", " ").title())
        sections.append(f"### {type_name}\n")
        
        for impact in impacts:
            file_path = impact.get("file_path", "unknown")
            severity = impact.get("severity", "unknown").upper()
            severity_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "⚪")
            sections.append(f"- {severity_emoji} **{file_path}** (Severity: {severity})")
        
        sections.append("")  # Empty line between groups
    
    return "\n".join(sections)


def _generate_required_changes(impact_analysis: list[dict]) -> str:
    """
    Generate required changes section.
    
    Details the specific changes needed for each impacted file,
    including impact description and suggested modifications.
    
    Args:
        impact_analysis: List of impact objects
        
    Returns:
        Markdown formatted detailed changes
    """
    sections = []
    
    for impact in impact_analysis:
        file_path = impact.get("file_path", "unknown")
        impact_type = impact.get("impact_type", "unknown")
        severity = impact.get("severity", "unknown")
        description = impact.get("description", "No description available")
        suggested_changes = impact.get("suggested_changes", [])
        
        sections.append(f"### {file_path}\n")
        sections.append(f"**Impact Type:** {impact_type.replace('_', ' ').title()}")
        sections.append(f"**Severity:** {severity.upper()}\n")
        sections.append(f"**Description:**")
        sections.append(f"{description}\n")
        sections.append(f"**Required Changes:**")
        
        for change in suggested_changes:
            sections.append(f"- {change}")
        
        sections.append("")  # Empty line between files
    
    return "\n".join(sections)


def _generate_acceptance_criteria(regulatory_model: dict, llm) -> str:
    """
    Generate acceptance criteria from regulatory requirements.
    
    Converts regulatory requirements into testable acceptance criteria
    that can be used to verify compliance.
    
    Args:
        regulatory_model: Structured regulatory model
        llm: LLM provider instance
        
    Returns:
        Markdown formatted acceptance criteria
    """
    requirements = regulatory_model.get("requirements", [])
    
    if not requirements:
        return "- All code changes must be reviewed and tested\n- System must maintain backward compatibility where possible"
    
    requirements_text = "\n".join(f"{i+1}. {req}" for i, req in enumerate(requirements))
    
    prompt = f"""Converta os seguintes requisitos regulatórios em critérios de aceitação testáveis.

REQUISITOS REGULATÓRIOS:
{requirements_text}

Para cada requisito, crie um critério de aceitação que:
- Seja específico e mensurável
- Possa ser testado/verificado
- Use formato "GIVEN/WHEN/THEN" ou "O sistema DEVE..."

Liste os critérios de aceitação (um por linha, começando com "-"):

Critérios:"""

    try:
        criteria = llm.generate(prompt, max_tokens=800)
        # Ensure criteria are formatted as bullet points
        lines = criteria.strip().split('\n')
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('-'):
                line = f"- {line}"
            if line:
                formatted_lines.append(line)
        
        return "\n".join(formatted_lines) if formatted_lines else "- Verify compliance with all regulatory requirements"
        
    except Exception as e:
        logger.error(f"LLM failed to generate acceptance criteria: {e}")
        # Fallback to simple criteria based on requirements
        criteria = []
        for req in requirements:
            criteria.append(f"- Verify implementation of: {req}")
        return "\n".join(criteria)


def _calculate_estimated_effort(impact_analysis: list[dict]) -> str:
    """
    Calculate estimated effort based on severity weights.
    
    Uses severity weights: high=3, medium=2, low=1
    Sums the weights and provides an effort estimate.
    
    Args:
        impact_analysis: List of impact objects
        
    Returns:
        Markdown formatted effort estimate
    """
    # Define severity weights
    severity_weights = {
        "high": 3,
        "medium": 2,
        "low": 1
    }
    
    # Count impacts by severity
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    total_weight = 0
    
    for impact in impact_analysis:
        severity = impact.get("severity", "medium").lower()
        if severity in severity_counts:
            severity_counts[severity] += 1
            total_weight += severity_weights[severity]
    
    # Calculate effort estimate
    # Rough estimate: each point = 1 day of work
    estimated_days = total_weight
    
    # Build effort summary
    effort_text = f"""**Total Effort Points:** {total_weight}

**Breakdown by Severity:**
- High Severity: {severity_counts['high']} files (×3 points = {severity_counts['high'] * 3} points)
- Medium Severity: {severity_counts['medium']} files (×2 points = {severity_counts['medium'] * 2} points)
- Low Severity: {severity_counts['low']} files (×1 point = {severity_counts['low'] * 1} points)

**Estimated Timeline:** {estimated_days} developer-days

**Recommendation:**
"""
    
    # Add recommendation based on total effort
    if total_weight <= 5:
        effort_text += "This is a small change that can likely be completed in a single sprint."
    elif total_weight <= 15:
        effort_text += "This is a medium-sized change requiring careful planning and testing across multiple sprints."
    else:
        effort_text += "This is a large change requiring significant effort. Consider breaking into phases and allocating multiple sprints."
    
    return effort_text


def _generate_minimal_spec(regulatory_model: dict) -> str:
    """
    Generate minimal specification when no impact analysis is available.
    
    Args:
        regulatory_model: Structured regulatory model
        
    Returns:
        Minimal technical specification
    """
    title = regulatory_model.get("title", "Technical Specification")
    description = regulatory_model.get("description", "No description available")
    
    spec = f"""# Technical Specification: {title}

## Overview

{description}

## Affected Components

No impacted components identified.

## Required Changes

No specific changes identified. Manual analysis required.

## Acceptance Criteria

- Review regulatory requirements manually
- Identify affected systems and components
- Implement necessary changes to ensure compliance

## Estimated Effort

Unable to estimate - no impact analysis available.
"""
    
    logger.info("Generated minimal technical spec (no impact analysis)")
    return spec
