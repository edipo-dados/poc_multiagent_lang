"""
Demonstration script for the Impact Agent.

This script shows how the Impact Agent analyzes code files and generates
technical impact assessments based on regulatory changes.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.agents.impact import impact_agent
from backend.models.state import GlobalState


def demo_impact_agent():
    """Demonstrate the Impact Agent with a sample regulatory change."""
    
    print("=" * 80)
    print("IMPACT AGENT DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Create a sample state with regulatory model and impacted files
    state = GlobalState(
        raw_regulatory_text="""
        Nova Resolução BCB 2024/001 - Atualização do Sistema Pix
        
        O Banco Central do Brasil estabelece novos requisitos para o sistema Pix:
        
        1. Todas as transações Pix devem incluir um identificador único de rastreabilidade
        2. Validação obrigatória de formato para chaves Pix (CPF, CNPJ, email, telefone)
        3. Implementação de limites de valor por tipo de transação
        4. Registro de auditoria completo para todas as operações
        
        Prazo de implementação: 31/12/2024
        Penalidades por não conformidade: Multa de até R$ 100.000,00
        """,
        regulatory_model={
            "title": "Resolução BCB 2024/001 - Atualização do Sistema Pix",
            "description": "Novos requisitos de rastreabilidade, validação e auditoria para transações Pix",
            "requirements": [
                "Incluir identificador único de rastreabilidade em todas as transações",
                "Implementar validação obrigatória de formato para chaves Pix",
                "Implementar limites de valor por tipo de transação",
                "Registrar auditoria completa para todas as operações"
            ],
            "deadlines": [
                {"date": "2024-12-31", "description": "Prazo de implementação obrigatória"}
            ],
            "affected_systems": ["Pix", "Pagamentos", "Auditoria"]
        },
        impacted_files=[
            {
                "file_path": "api/endpoints.py",
                "relevance_score": 0.92,
                "snippet": "FastAPI endpoints for Pix operations"
            },
            {
                "file_path": "api/schemas.py",
                "relevance_score": 0.88,
                "snippet": "Pydantic schemas for API requests and responses"
            },
            {
                "file_path": "domain/validators.py",
                "relevance_score": 0.85,
                "snippet": "Business rule validators for Pix transactions"
            },
            {
                "file_path": "database/models.py",
                "relevance_score": 0.80,
                "snippet": "SQLAlchemy ORM models for database"
            }
        ],
        execution_id="demo-001"
    )
    
    print("INPUT:")
    print("-" * 80)
    print(f"Regulatory Title: {state.regulatory_model['title']}")
    print(f"Requirements: {len(state.regulatory_model['requirements'])} items")
    print(f"Impacted Files: {len(state.impacted_files)} files")
    print()
    
    print("ANALYZING IMPACTS...")
    print("-" * 80)
    
    # Note: This will use the actual LLM if configured, or fallback implementation
    try:
        result = impact_agent(state)
        
        if result.error:
            print(f"ERROR: {result.error}")
            return
        
        print(f"✓ Analysis completed successfully")
        print(f"✓ Generated {len(result.impact_analysis)} impact assessments")
        print()
        
        print("IMPACT ANALYSIS RESULTS:")
        print("=" * 80)
        
        for i, impact in enumerate(result.impact_analysis, 1):
            print(f"\n{i}. {impact['file_path']}")
            print(f"   Impact Type: {impact['impact_type'].upper()}")
            print(f"   Severity: {impact['severity'].upper()}")
            print(f"   Description: {impact['description'][:100]}...")
            print(f"   Suggested Changes: {len(impact['suggested_changes'])} items")
            for j, change in enumerate(impact['suggested_changes'][:3], 1):
                print(f"      {j}. {change}")
            if len(impact['suggested_changes']) > 3:
                print(f"      ... and {len(impact['suggested_changes']) - 3} more")
        
        print()
        print("=" * 80)
        print("DEMONSTRATION COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Set environment variable to use fallback LLM for demo
    os.environ["LLM_TYPE"] = "local"
    
    demo_impact_agent()
