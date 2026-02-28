"""
Streamlit Frontend for Regulatory AI POC

This application provides a web interface for analyzing regulatory text
and visualizing the multi-agent analysis results.
"""

import os
import streamlit as st
import requests
import json
from typing import Optional

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 120  # 2 minutes for long-running analysis

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.analysis_result = None


def analyze_text(regulatory_text: str, gemini_api_key: Optional[str] = None) -> dict:
    """
    Call backend API to analyze regulatory text.
    
    Args:
        regulatory_text: The regulatory text to analyze
        
    Returns:
        dict: Analysis results from backend
        
    Raises:
        requests.Timeout: If request exceeds timeout
        requests.RequestException: If network error occurs
        Exception: For other errors
    """
    try:
        # Prepare request payload
        payload = {"regulatory_text": regulatory_text}
        
        # Add custom headers if API key is provided
        headers = {'Content-Type': 'application/json'}
        if gemini_api_key:
            headers['X-Gemini-API-Key'] = gemini_api_key
        
        response = requests.post(
            f"{BACKEND_URL}/analyze",
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise ValueError(f"Entrada inválida: {response.json().get('detail', 'Erro desconhecido')}")
        elif response.status_code == 500:
            raise Exception(f"Erro no servidor: {response.json().get('detail', 'Erro interno')}")
        else:
            raise Exception(f"Erro inesperado: {response.status_code}")
            
    except requests.Timeout:
        raise requests.Timeout("A análise excedeu o tempo limite de 2 minutos")
    except requests.ConnectionError:
        raise requests.ConnectionError("Não foi possível conectar ao backend")
    except requests.RequestException as e:
        raise requests.RequestException(f"Erro de rede: {str(e)}")


def render_input_section():
    """Render the input section with text area and submit button."""
    st.title("Análise de Impacto Regulatório - POC")
    st.markdown("""
    Este sistema analisa texto regulatório e identifica impactos em código de serviço Pix
    usando uma arquitetura multi-agente determinística.
    """)
    
    # Gemini API Key input (collapsible)
    with st.expander("⚙️ Configuração da API Key (Gemini)", expanded=False):
        st.markdown("""
        Para usar este sistema, você precisa de uma API key do Google Gemini.
        
        **Como obter:**
        1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Clique em "Create API Key"
        3. Cole a key abaixo
        """)
        
        gemini_api_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIzaSy...",
            help="Sua chave de API do Google Gemini. Será usada apenas para esta sessão."
        )
        
        if gemini_api_key:
            st.success("✅ API Key configurada!")
        else:
            st.warning("⚠️ API Key não configurada. A análise usará a key padrão do servidor (se disponível).")
    
    # Text input area
    regulatory_text = st.text_area(
        "Texto Regulatório",
        height=200,
        placeholder="Cole aqui o texto regulatório para análise...",
        help="Insira o texto da regulação que deseja analisar"
    )
    
    # Submit button
    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_button = st.button("Analisar Impacto", type="primary", use_container_width=True)
    
    return regulatory_text, analyze_button, gemini_api_key


def render_regulatory_model_tab(regulatory_model: dict):
    """Render tab 1: Modelo Regulatório Estruturado."""
    st.subheader("Modelo Regulatório Estruturado")
    st.markdown("Estrutura formal extraída do texto regulatório:")
    
    # Display as formatted JSON
    st.json(regulatory_model)


def render_impact_analysis_tab(impact_analysis: list):
    """Render tab 2: Impacto no Código."""
    st.subheader("Impacto no Código")
    
    if not impact_analysis:
        st.info("Nenhum impacto identificado no código.")
        return
    
    st.markdown(f"**Total de impactos identificados:** {len(impact_analysis)}")
    
    # Group by severity
    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for impact in impact_analysis:
        severity = impact.get("severity", "low")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Display severity summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Alta Severidade", severity_counts["high"])
    with col2:
        st.metric("Média Severidade", severity_counts["medium"])
    with col3:
        st.metric("Baixa Severidade", severity_counts["low"])
    
    st.markdown("---")
    
    # Display each impact with expandable sections
    for idx, impact in enumerate(impact_analysis, 1):
        file_path = impact.get("file_path", "Desconhecido")
        severity = impact.get("severity", "low").upper()
        impact_type = impact.get("impact_type", "unknown")
        
        # Color code by severity
        severity_emoji = {
            "HIGH": "🔴",
            "MEDIUM": "🟡",
            "LOW": "🟢"
        }.get(severity, "⚪")
        
        with st.expander(f"{severity_emoji} {file_path} - {severity}"):
            st.markdown(f"**Tipo de Impacto:** `{impact_type}`")
            st.markdown(f"**Severidade:** `{severity}`")
            
            description = impact.get("description", "Sem descrição")
            st.markdown(f"**Descrição:**\n{description}")
            
            suggested_changes = impact.get("suggested_changes", [])
            if suggested_changes:
                st.markdown("**Mudanças Sugeridas:**")
                for change in suggested_changes:
                    st.markdown(f"- {change}")


def render_technical_spec_tab(technical_spec: str):
    """Render tab 3: Especificação Técnica."""
    st.subheader("Especificação Técnica")
    
    if not technical_spec:
        st.info("Especificação técnica não disponível.")
        return
    
    # Render as Markdown
    st.markdown(technical_spec)


def render_kiro_prompt_tab(kiro_prompt: str):
    """Render tab 4: Prompt Final para Desenvolvimento."""
    st.subheader("Prompt Final para Desenvolvimento")
    
    if not kiro_prompt:
        st.info("Prompt de desenvolvimento não disponível.")
        return
    
    st.markdown("Este prompt pode ser usado diretamente para implementar as mudanças necessárias:")
    
    # Display as text with copy button
    st.text_area(
        "Prompt",
        value=kiro_prompt,
        height=400,
        label_visibility="collapsed"
    )


def render_graph_visualization_tab(results: dict):
    """Render tab 5: Fluxo de Execução dos Agentes."""
    st.subheader("Fluxo de Execução dos Agentes")
    
    # Display execution metadata
    col1, col2 = st.columns(2)
    with col1:
        execution_id = results.get("execution_id", "N/A")
        st.markdown(f"**ID da Execução:** `{execution_id}`")
    with col2:
        timestamp = results.get("timestamp", "N/A")
        st.markdown(f"**Timestamp:** `{timestamp}`")
    
    # Display summary metrics
    st.markdown("---")
    st.markdown("### Resumo da Análise")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        change_detected = results.get("change_detected", False)
        st.metric("Mudança Detectada", "Sim" if change_detected else "Não")
    with col2:
        risk_level = results.get("risk_level", "unknown").upper()
        st.metric("Nível de Risco", risk_level)
    with col3:
        impacted_files_count = len(results.get("impacted_files", []))
        st.metric("Arquivos Impactados", impacted_files_count)
    
    st.markdown("---")
    
    # Render Mermaid diagram
    graph_visualization = results.get("graph_visualization", "")
    
    if graph_visualization:
        st.markdown("### Diagrama de Fluxo dos Agentes")
        
        # Use Streamlit components to render Mermaid
        import streamlit.components.v1 as components
        
        # Escape the Mermaid code properly for HTML
        mermaid_code = graph_visualization.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        mermaid_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script type="module">
                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                mermaid.initialize({{ 
                    startOnLoad: true, 
                    theme: 'default',
                    flowchart: {{
                        useMaxWidth: true,
                        htmlLabels: true,
                        curve: 'basis'
                    }}
                }});
            </script>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background: white;
                    font-family: Arial, sans-serif;
                }}
                .mermaid {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 400px;
                }}
            </style>
        </head>
        <body>
            <pre class="mermaid">
{mermaid_code}
            </pre>
        </body>
        </html>
        """
        
        components.html(mermaid_html, height=600, scrolling=True)
    else:
        st.info("Visualização do grafo não disponível.")


def render_results_tabs(results: dict):
    """Render the 5-tab results section."""
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Modelo Regulatório Estruturado",
        "💻 Impacto no Código",
        "📝 Especificação Técnica",
        "🚀 Prompt Final para Desenvolvimento",
        "🔄 Fluxo de Execução dos Agentes"
    ])
    
    with tab1:
        regulatory_model = results.get("regulatory_model", {})
        render_regulatory_model_tab(regulatory_model)
    
    with tab2:
        impact_analysis = results.get("impact_analysis", [])
        render_impact_analysis_tab(impact_analysis)
    
    with tab3:
        technical_spec = results.get("technical_spec", "")
        render_technical_spec_tab(technical_spec)
    
    with tab4:
        kiro_prompt = results.get("kiro_prompt", "")
        render_kiro_prompt_tab(kiro_prompt)
    
    with tab5:
        render_graph_visualization_tab(results)


def main():
    """Main application entry point."""
    # Set page configuration
    st.set_page_config(
        page_title="Regulatory AI POC",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state['results'] = None
    if 'error' not in st.session_state:
        st.session_state['error'] = None
    
    # Render input section
    regulatory_text, analyze_button, gemini_api_key = render_input_section()
    
    # Handle analysis submission
    if analyze_button:
        # Validate input
        if not regulatory_text or not regulatory_text.strip():
            st.error("❌ Por favor, insira um texto regulatório.")
            st.session_state['results'] = None
            st.session_state['error'] = None
        else:
            # Clear previous results and errors
            st.session_state['results'] = None
            st.session_state['error'] = None
            
            # Show loading indicator and perform analysis
            with st.spinner("🔄 Analisando... Isso pode levar alguns segundos."):
                try:
                    results = analyze_text(regulatory_text, gemini_api_key)
                    st.session_state['results'] = results
                    st.session_state['error'] = None
                    st.success("✅ Análise concluída com sucesso!")
                    
                except requests.Timeout:
                    error_msg = "⏱️ A análise excedeu o tempo limite de 2 minutos. Tente com um texto menor."
                    st.error(error_msg)
                    st.session_state['error'] = error_msg
                    
                except requests.ConnectionError:
                    error_msg = "🔌 Não foi possível conectar ao backend. Verifique se o serviço está rodando."
                    st.error(error_msg)
                    st.session_state['error'] = error_msg
                    
                    # Offer retry option
                    if st.button("🔄 Tentar Novamente"):
                        st.rerun()
                    
                except ValueError as e:
                    error_msg = f"❌ {str(e)}"
                    st.error(error_msg)
                    st.session_state['error'] = error_msg
                    
                except Exception as e:
                    error_msg = f"❌ Erro inesperado: {str(e)}"
                    st.error(error_msg)
                    st.session_state['error'] = error_msg
                    
                    # Offer retry option
                    if st.button("🔄 Tentar Novamente"):
                        st.rerun()
    
    # Display results if available
    if st.session_state.get('results'):
        st.markdown("---")
        render_results_tabs(st.session_state['results'])
    
    # Display footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Regulatory AI POC - Sistema Multi-Agente para Análise de Impacto Regulatório
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
