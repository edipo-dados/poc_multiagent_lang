"""
KiroPrompt Agent - Development Prompt Generation

The KiroPrompt Agent generates a deterministic development prompt (kiro_prompt)
that provides executable instructions for implementing the regulatory changes.
It extracts context from the regulatory model, generates step-by-step instructions
from the impact analysis, lists file modifications, and creates validation steps.

Requirements: 8.1, 8.2, 8.3, 8.4
"""

import logging
from typing import Optional
from backend.models.state import GlobalState


logger = logging.getLogger(__name__)


def kiro_prompt_agent(state: GlobalState) -> GlobalState:
    """
    Generate development prompt with executable instructions.
    
    This agent performs the sixth and final step in the multi-agent pipeline:
    1. Extract context from regulatory_model
    2. Generate step-by-step instructions from impact_analysis
    3. List file modifications with specific changes
    4. Create validation steps from technical_spec acceptance criteria
    5. Add standard constraints
    6. Format as plain text prompt
    7. Update Global State with kiro_prompt
    
    Args:
        state: GlobalState containing regulatory_model, impact_analysis, and technical_spec
        
    Returns:
        Updated GlobalState with kiro_prompt populated
        
    Raises:
        Exception: If prompt generation fails
        
    Requirements:
        - 8.1: Generate kiro_prompt for development
        - 8.2: Include context, specific_instructions, file_modifications, validation_steps
        - 8.3: Reference technical_spec and impact_analysis
        - 8.4: Format as executable instructions
    """
    logger.info(f"KiroPrompt Agent starting for execution {state.execution_id}")
    
    try:
        # Validate prerequisites
        if not state.regulatory_model:
            raise ValueError("regulatory_model is required but not set")
        
        if not state.technical_spec:
            logger.warning("technical_spec not available - generating minimal prompt")
        
        if not state.impact_analysis:
            logger.warning("impact_analysis not available - generating minimal prompt")
        
        # Generate kiro prompt
        kiro_prompt = _generate_kiro_prompt(
            regulatory_model=state.regulatory_model,
            impact_analysis=state.impact_analysis,
            technical_spec=state.technical_spec
        )
        
        # Update state with kiro prompt
        state.kiro_prompt = kiro_prompt
        
        logger.info(f"KiroPrompt Agent completed successfully. Prompt length: {len(kiro_prompt)} chars")
        return state
        
    except Exception as e:
        logger.error(f"KiroPrompt Agent failed: {str(e)}", exc_info=True)
        state.error = f"KiroPrompt Agent error: {str(e)}"
        raise


def _generate_kiro_prompt(
    regulatory_model: dict,
    impact_analysis: list[dict],
    technical_spec: Optional[str]
) -> str:
    """
    Generate complete Kiro development prompt.
    
    Creates a structured prompt with sections:
    - CONTEXT: Regulatory requirement summary
    - OBJECTIVE: Clear goal statement
    - SPECIFIC INSTRUCTIONS: Step-by-step implementation guide
    - FILE MODIFICATIONS: Detailed changes per file
    - VALIDATION STEPS: Testing and verification criteria
    - CONSTRAINTS: Development guidelines
    
    Args:
        regulatory_model: Structured regulatory model
        impact_analysis: List of impact objects
        technical_spec: Technical specification document
        
    Returns:
        Complete kiro prompt as plain text string
    """
    # Generate each section
    context = _generate_context(regulatory_model)
    objective = _generate_objective(regulatory_model)
    specific_instructions = _generate_specific_instructions(impact_analysis)
    file_modifications = _generate_file_modifications(impact_analysis)
    validation_steps = _generate_validation_steps(technical_spec, regulatory_model)
    constraints = _generate_constraints()
    
    # Assemble the complete prompt
    prompt = f"""CONTEXT:
{context}

OBJECTIVE:
{objective}

SPECIFIC INSTRUCTIONS:
{specific_instructions}

FILE MODIFICATIONS:
{file_modifications}

VALIDATION STEPS:
{validation_steps}

CONSTRAINTS:
{constraints}
"""
    
    logger.debug(f"Generated kiro prompt with {len(prompt)} characters")
    return prompt


def _generate_context(regulatory_model: dict) -> str:
    """
    Generate context section from regulatory model.
    
    Provides background on the regulatory change, including title,
    description, key requirements, and deadlines.
    
    Args:
        regulatory_model: Structured regulatory model
        
    Returns:
        Context text
    """
    title = regulatory_model.get("title", "Regulatory Change")
    description = regulatory_model.get("description", "No description available")
    requirements = regulatory_model.get("requirements", [])
    deadlines = regulatory_model.get("deadlines", [])
    affected_systems = regulatory_model.get("affected_systems", [])
    
    context_parts = [
        f"Regulatory Change: {title}",
        "",
        f"Description: {description}",
    ]
    
    if requirements:
        context_parts.append("")
        context_parts.append("Key Requirements:")
        for i, req in enumerate(requirements, 1):
            context_parts.append(f"{i}. {req}")
    
    if deadlines:
        context_parts.append("")
        context_parts.append("Deadlines:")
        for deadline in deadlines:
            date = deadline.get("date", "N/A")
            desc = deadline.get("description", "N/A")
            context_parts.append(f"- {date}: {desc}")
    
    if affected_systems:
        systems_text = ", ".join(affected_systems)
        context_parts.append("")
        context_parts.append(f"Affected Systems: {systems_text}")
    
    return "\n".join(context_parts)


def _generate_objective(regulatory_model: dict) -> str:
    """
    Generate objective section.
    
    Creates a clear, concise objective statement for the implementation.
    
    Args:
        regulatory_model: Structured regulatory model
        
    Returns:
        Objective text
    """
    title = regulatory_model.get("title", "regulatory requirements")
    
    objective = f"Implement changes to comply with {title}"
    
    return objective


def _generate_specific_instructions(impact_analysis: list[dict]) -> str:
    """
    Generate step-by-step instructions from impact analysis.
    
    Creates numbered instructions derived from the impact analysis,
    organized by impact type and severity.
    
    Args:
        impact_analysis: List of impact objects
        
    Returns:
        Numbered instruction list
    """
    if not impact_analysis:
        return "1. Review regulatory requirements manually\n2. Identify affected code components\n3. Implement necessary changes"
    
    # Sort impacts by severity (high -> medium -> low) for prioritization
    severity_order = {"high": 0, "medium": 1, "low": 2}
    sorted_impacts = sorted(
        impact_analysis,
        key=lambda x: severity_order.get(x.get("severity", "medium").lower(), 1)
    )
    
    instructions = []
    step_num = 1
    
    # Group by impact type for better organization
    impact_types = {}
    for impact in sorted_impacts:
        impact_type = impact.get("impact_type", "unknown")
        if impact_type not in impact_types:
            impact_types[impact_type] = []
        impact_types[impact_type].append(impact)
    
    # Generate instructions for each impact type
    type_names = {
        "schema_change": "Database Schema Changes",
        "business_logic": "Business Logic Updates",
        "validation": "Validation Rule Updates",
        "api_contract": "API Contract Modifications"
    }
    
    for impact_type, impacts in impact_types.items():
        type_name = type_names.get(impact_type, impact_type.replace("_", " ").title())
        instructions.append(f"{step_num}. {type_name}:")
        step_num += 1
        
        for impact in impacts:
            file_path = impact.get("file_path", "unknown")
            severity = impact.get("severity", "medium").upper()
            description = impact.get("description", "")
            
            instructions.append(f"   - [{severity}] {file_path}")
            if description:
                # Add description as indented text
                instructions.append(f"     {description}")
        
        instructions.append("")  # Empty line between groups
    
    # Add final steps
    instructions.append(f"{step_num}. Run all existing tests to ensure no regressions")
    step_num += 1
    instructions.append(f"{step_num}. Add new tests to cover regulatory compliance scenarios")
    step_num += 1
    instructions.append(f"{step_num}. Update documentation to reflect changes")
    
    return "\n".join(instructions)


def _generate_file_modifications(impact_analysis: list[dict]) -> str:
    """
    Generate file modifications section.
    
    Lists each file with specific changes needed, extracted from
    the suggested_changes in the impact analysis.
    
    Args:
        impact_analysis: List of impact objects
        
    Returns:
        File modification list
    """
    if not impact_analysis:
        return "No specific file modifications identified. Manual analysis required."
    
    modifications = []
    
    for impact in impact_analysis:
        file_path = impact.get("file_path", "unknown")
        impact_type = impact.get("impact_type", "unknown")
        severity = impact.get("severity", "medium")
        suggested_changes = impact.get("suggested_changes", [])
        
        # File header
        modifications.append(f"- {file_path} ({impact_type}, {severity} severity):")
        
        # List suggested changes
        if suggested_changes:
            for change in suggested_changes:
                modifications.append(f"  * {change}")
        else:
            modifications.append(f"  * Review and update as needed")
        
        modifications.append("")  # Empty line between files
    
    return "\n".join(modifications)


def _generate_validation_steps(technical_spec: Optional[str], regulatory_model: dict) -> str:
    """
    Generate validation steps from technical spec and regulatory model.
    
    Extracts acceptance criteria from the technical spec if available,
    otherwise generates validation steps from regulatory requirements.
    
    Args:
        technical_spec: Technical specification document
        regulatory_model: Structured regulatory model
        
    Returns:
        Numbered validation steps
    """
    validation_steps = []
    step_num = 1
    
    # Try to extract acceptance criteria from technical spec
    if technical_spec:
        criteria = _extract_acceptance_criteria(technical_spec)
        if criteria:
            for criterion in criteria:
                validation_steps.append(f"{step_num}. {criterion}")
                step_num += 1
    
    # If no criteria extracted, generate from regulatory requirements
    if not validation_steps:
        requirements = regulatory_model.get("requirements", [])
        if requirements:
            for req in requirements:
                validation_steps.append(f"{step_num}. Verify implementation of: {req}")
                step_num += 1
    
    # Add standard validation steps
    if not validation_steps:
        validation_steps.append(f"{step_num}. Verify all code changes are implemented correctly")
        step_num += 1
    
    validation_steps.append(f"{step_num}. Verify compliance with regulatory requirements")
    step_num += 1
    validation_steps.append(f"{step_num}. Run existing test suite and ensure all tests pass")
    step_num += 1
    validation_steps.append(f"{step_num}. Perform manual testing of affected functionality")
    step_num += 1
    validation_steps.append(f"{step_num}. Review changes with compliance team")
    
    return "\n".join(validation_steps)


def _extract_acceptance_criteria(technical_spec: str) -> list[str]:
    """
    Extract acceptance criteria from technical specification.
    
    Looks for the "Acceptance Criteria" section in the markdown
    and extracts bullet points.
    
    Args:
        technical_spec: Technical specification markdown
        
    Returns:
        List of acceptance criteria strings
    """
    criteria = []
    
    # Find the Acceptance Criteria section
    lines = technical_spec.split('\n')
    in_criteria_section = False
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if we're entering the acceptance criteria section
        if "## Acceptance Criteria" in line or "## acceptance criteria" in line.lower():
            in_criteria_section = True
            continue
        
        # Check if we're leaving the section (next ## header)
        if in_criteria_section and line_stripped.startswith("##"):
            break
        
        # Extract criteria (bullet points)
        if in_criteria_section and line_stripped.startswith("-"):
            criterion = line_stripped.lstrip("- ").strip()
            if criterion:
                criteria.append(criterion)
    
    logger.debug(f"Extracted {len(criteria)} acceptance criteria from technical spec")
    return criteria


def _generate_constraints() -> str:
    """
    Generate standard constraints section.
    
    Provides development guidelines and best practices to follow
    during implementation.
    
    Returns:
        Constraints text
    """
    constraints = [
        "- Maintain backward compatibility where possible",
        "- Follow existing code patterns and conventions",
        "- Update documentation for all changes",
        "- Ensure all changes are properly tested",
        "- Add comments explaining regulatory compliance logic",
        "- Consider performance implications of changes",
        "- Ensure error handling is robust",
        "- Follow security best practices",
        "- Keep changes minimal and focused on requirements"
    ]
    
    return "\n".join(constraints)
