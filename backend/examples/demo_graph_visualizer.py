"""
Demo script for GraphVisualizer service.

Demonstrates how to use the GraphVisualizer to generate Mermaid diagrams
from Global State after agent execution.

Usage:
    python -m backend.examples.demo_graph_visualizer
"""

import sys
from pathlib import Path
from datetime import datetime, UTC

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.models.state import GlobalState
from backend.services.graph_visualizer import GraphVisualizer


def create_sample_state() -> GlobalState:
    """Create a sample GlobalState with realistic data."""
    return GlobalState(
        raw_regulatory_text="""
        Resolução BCB nº 999/2024
        
        Altera os limites de transações Pix para pessoas físicas.
        
        Art. 1º O limite diário de transações Pix para pessoas físicas passa a ser de R$ 5.000,00.
        
        Art. 2º Esta resolução entra em vigor em 31 de dezembro de 2024.
        """,
        change_detected=True,
        risk_level="high",
        regulatory_model={
            "title": "Resolução BCB nº 999/2024 - Novos Limites Pix",
            "description": "Altera os limites de transações Pix para pessoas físicas",
            "requirements": [
                "Aumentar limite diário para R$ 5.000,00",
                "Atualizar validações de limite",
                "Modificar mensagens de erro"
            ],
            "deadlines": [
                {
                    "date": "2024-12-31",
                    "description": "Entrada em vigor da nova resolução"
                }
            ],
            "affected_systems": ["Pix", "Validações", "API"]
        },
        impacted_files=[
            {
                "file_path": "api/endpoints.py",
                "relevance_score": 0.95,
                "snippet": "@router.post('/pix')..."
            },
            {
                "file_path": "domain/validators.py",
                "relevance_score": 0.92,
                "snippet": "def validate_pix_amount..."
            },
            {
                "file_path": "api/schemas.py",
                "relevance_score": 0.87,
                "snippet": "class PixCreateRequest..."
            }
        ],
        impact_analysis=[
            {
                "file_path": "api/endpoints.py",
                "impact_type": "api_contract",
                "severity": "medium",
                "description": "Endpoint de criação de Pix precisa validar novo limite",
                "suggested_changes": [
                    "Atualizar constante MAX_PIX_AMOUNT para 5000.00",
                    "Adicionar validação de limite no endpoint"
                ]
            },
            {
                "file_path": "domain/validators.py",
                "impact_type": "validation",
                "severity": "high",
                "description": "Validador de valor Pix precisa ser atualizado",
                "suggested_changes": [
                    "Modificar função validate_pix_amount",
                    "Atualizar mensagem de erro de limite excedido"
                ]
            },
            {
                "file_path": "api/schemas.py",
                "impact_type": "schema_change",
                "severity": "low",
                "description": "Schema pode precisar de atualização na documentação",
                "suggested_changes": [
                    "Atualizar docstring com novo limite",
                    "Adicionar exemplo com valor próximo ao limite"
                ]
            }
        ],
        technical_spec="""# Especificação Técnica: Resolução BCB nº 999/2024

## Visão Geral
Implementar novos limites de transação Pix conforme Resolução BCB nº 999/2024.

## Componentes Afetados
- api/endpoints.py (API Contract - Média)
- domain/validators.py (Validation - Alta)
- api/schemas.py (Schema Change - Baixa)

## Mudanças Necessárias
### api/endpoints.py
- Atualizar constante MAX_PIX_AMOUNT para 5000.00
- Adicionar validação de limite no endpoint

### domain/validators.py
- Modificar função validate_pix_amount
- Atualizar mensagem de erro de limite excedido

## Critérios de Aceitação
- Limite diário de R$ 5.000,00 implementado
- Validações atualizadas
- Testes passando

## Esforço Estimado
6 pontos (2 alta + 2 média + 1 baixa)
""",
        kiro_prompt="""CONTEXT:
Resolução BCB nº 999/2024 altera limites de transações Pix para R$ 5.000,00.

OBJECTIVE:
Implementar novos limites de transação Pix conforme regulação do Banco Central.

SPECIFIC INSTRUCTIONS:
1. Atualizar constante MAX_PIX_AMOUNT em api/endpoints.py para 5000.00
2. Modificar função validate_pix_amount em domain/validators.py
3. Atualizar mensagens de erro de limite excedido
4. Atualizar documentação em api/schemas.py

FILE MODIFICATIONS:
- api/endpoints.py: Atualizar MAX_PIX_AMOUNT para 5000.00
- domain/validators.py: Modificar validate_pix_amount e mensagens de erro
- api/schemas.py: Atualizar docstring com novo limite

VALIDATION STEPS:
1. Verificar que transações até R$ 5.000,00 são aceitas
2. Verificar que transações acima de R$ 5.000,00 são rejeitadas
3. Executar suite de testes existente
4. Validar conformidade com requisitos regulatórios

CONSTRAINTS:
- Manter compatibilidade retroativa onde possível
- Seguir padrões de código existentes
- Atualizar documentação
""",
        execution_id="demo-12345",
        execution_timestamp=datetime.now(UTC)
    )


def main():
    """Main demo function."""
    print("=" * 80)
    print("GraphVisualizer Demo")
    print("=" * 80)
    print()
    
    # Create sample state
    print("Creating sample Global State...")
    state = create_sample_state()
    print(f"✓ State created with execution_id: {state.execution_id}")
    print(f"  - Change detected: {state.change_detected}")
    print(f"  - Risk level: {state.risk_level}")
    print(f"  - Impacted files: {len(state.impacted_files)}")
    print(f"  - Impact analysis: {len(state.impact_analysis)}")
    print()
    
    # Create visualizer
    print("Initializing GraphVisualizer...")
    visualizer = GraphVisualizer()
    print("✓ GraphVisualizer initialized")
    print()
    
    # Generate Mermaid diagram
    print("Generating Mermaid diagram...")
    diagram = visualizer.generate_mermaid_diagram(state)
    print("✓ Mermaid diagram generated")
    print()
    
    # Display diagram
    print("=" * 80)
    print("Generated Mermaid Diagram:")
    print("=" * 80)
    print(diagram)
    print()
    
    # Verify diagram structure
    print("=" * 80)
    print("Diagram Verification:")
    print("=" * 80)
    print(f"✓ Contains 'graph LR': {diagram.startswith('graph LR')}")
    print(f"✓ Contains Sentinel Agent: {'Sentinel Agent' in diagram}")
    print(f"✓ Contains Translator Agent: {'Translator Agent' in diagram}")
    print(f"✓ Contains CodeReader Agent: {'CodeReader Agent' in diagram}")
    print(f"✓ Contains Impact Agent: {'Impact Agent' in diagram}")
    print(f"✓ Contains SpecGenerator Agent: {'SpecGenerator Agent' in diagram}")
    print(f"✓ Contains KiroPrompt Agent: {'KiroPrompt Agent' in diagram}")
    print(f"✓ Contains execution flow arrows: {diagram.count('-->') == 7}")
    print()
    
    # Test PNG export (will gracefully fail if mmdc not available)
    print("=" * 80)
    print("Testing PNG Export:")
    print("=" * 80)
    print("Attempting to export diagram as PNG...")
    png_bytes = visualizer.export_png(diagram)
    
    if png_bytes:
        print(f"✓ PNG export successful! Generated {len(png_bytes)} bytes")
        print("  Note: mmdc (mermaid-cli) is installed and working")
    else:
        print("ℹ PNG export not available (mmdc not installed)")
        print("  This is expected if mermaid-cli is not installed")
        print("  Install with: npm install -g @mermaid-js/mermaid-cli")
    print()
    
    print("=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
