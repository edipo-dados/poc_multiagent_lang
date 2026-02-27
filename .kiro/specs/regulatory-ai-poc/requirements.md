# Requirements Document

## Introduction

Este documento especifica os requisitos para o regulatory-ai-poc, uma prova de conceito de arquitetura multi-agente que analisa texto regulatório, identifica impactos em código de serviço Pix, e gera especificações técnicas e prompts para desenvolvimento. O sistema opera completamente local usando LangGraph para orquestração determinística de agentes.

## Glossary

- **System**: O sistema regulatory-ai-poc completo
- **Frontend**: Interface web Streamlit para entrada de dados e visualização de resultados
- **Backend**: API FastAPI que orquestra os agentes e processa requisições
- **LangGraph_Orchestrator**: Componente que gerencia o fluxo determinístico de execução dos agentes
- **Sentinel_Agent**: Agente que detecta mudanças e avalia nível de risco do texto regulatório
- **Translator_Agent**: Agente que estrutura o texto regulatório em modelo formal
- **CodeReader_Agent**: Agente que analisa o repositório de código usando busca semântica
- **Impact_Agent**: Agente que identifica impactos técnicos no código
- **SpecGenerator_Agent**: Agente que gera especificação técnica estruturada
- **KiroPrompt_Agent**: Agente que gera prompt determinístico para desenvolvimento
- **Global_State**: Objeto de estado compartilhado entre todos os agentes
- **Vector_Store**: PostgreSQL com pgvector para armazenamento de embeddings
- **Pix_Repository**: Repositório fake simulando serviço Pix
- **Audit_Log**: Registro persistente de execuções para auditoria
- **Graph_Visualizer**: Componente que gera visualização do grafo de agentes

## Requirements

### Requirement 1: Manual Regulatory Text Input

**User Story:** Como analista regulatório, eu quero inserir texto regulatório manualmente via interface web, para que eu possa iniciar a análise de impacto sem depender de integrações externas.

#### Acceptance Criteria

1. THE Frontend SHALL provide a text area component for regulatory text input
2. THE Frontend SHALL provide a button labeled "Analisar Impacto" to trigger analysis
3. WHEN the user clicks "Analisar Impacto", THE Frontend SHALL send the regulatory text to the Backend via POST /analyze endpoint
4. THE Frontend SHALL display a loading indicator while analysis is in progress
5. IF the text area is empty, THEN THE Frontend SHALL display a validation error message

### Requirement 2: Multi-Agent Orchestration

**User Story:** Como desenvolvedor do sistema, eu quero uma orquestração determinística de agentes, para que o fluxo de execução seja previsível e auditável.

#### Acceptance Criteria

1. THE LangGraph_Orchestrator SHALL execute agents in the following fixed sequence: Sentinel_Agent → Translator_Agent → CodeReader_Agent → Impact_Agent → SpecGenerator_Agent → KiroPrompt_Agent
2. THE LangGraph_Orchestrator SHALL pass the Global_State between consecutive agents
3. WHEN an agent completes execution, THE LangGraph_Orchestrator SHALL automatically trigger the next agent in sequence
4. THE LangGraph_Orchestrator SHALL update the Global_State after each agent execution
5. IF an agent fails, THEN THE LangGraph_Orchestrator SHALL log the error and halt execution

### Requirement 3: Sentinel Agent Processing

**User Story:** Como analista regulatório, eu quero que o sistema detecte mudanças e avalie riscos no texto regulatório, para que eu possa priorizar ações.

#### Acceptance Criteria

1. WHEN the Sentinel_Agent receives regulatory text, THE Sentinel_Agent SHALL analyze the text for regulatory changes
2. THE Sentinel_Agent SHALL set the change_detected field in Global_State to true or false
3. THE Sentinel_Agent SHALL determine a risk_level value of "low", "medium", or "high"
4. THE Sentinel_Agent SHALL update the Global_State with change_detected and risk_level values
5. THE Sentinel_Agent SHALL complete execution within 10 seconds for texts up to 10000 characters

### Requirement 4: Translator Agent Processing

**User Story:** Como analista técnico, eu quero que o texto regulatório seja estruturado em modelo formal, para que eu possa compreender os requisitos de forma clara.

#### Acceptance Criteria

1. WHEN the Translator_Agent receives the Global_State, THE Translator_Agent SHALL extract structured information from raw_regulatory_text
2. THE Translator_Agent SHALL create a regulatory_model containing fields: title, description, requirements, deadlines, and affected_systems
3. THE Translator_Agent SHALL update the Global_State with the regulatory_model
4. THE regulatory_model SHALL be formatted as valid JSON
5. FOR ALL regulatory texts, translating then formatting then parsing SHALL produce an equivalent regulatory_model object (round-trip property)

### Requirement 5: Code Reader Agent Processing

**User Story:** Como desenvolvedor, eu quero que o sistema identifique arquivos relevantes no repositório, para que eu saiba onde fazer mudanças.

#### Acceptance Criteria

1. WHEN the CodeReader_Agent receives the Global_State, THE CodeReader_Agent SHALL perform semantic search on the Vector_Store using the regulatory_model
2. THE CodeReader_Agent SHALL retrieve the top 10 most relevant code files from the Pix_Repository
3. THE CodeReader_Agent SHALL update the Global_State with the impacted_files list containing file paths and relevance scores
4. THE CodeReader_Agent SHALL use embeddings stored in the Vector_Store for similarity matching
5. IF no relevant files are found, THEN THE CodeReader_Agent SHALL return an empty impacted_files list

### Requirement 6: Impact Analysis Agent Processing

**User Story:** Como arquiteto de software, eu quero uma análise detalhada de impactos técnicos, para que eu possa planejar as mudanças necessárias.

#### Acceptance Criteria

1. WHEN the Impact_Agent receives the Global_State, THE Impact_Agent SHALL analyze each file in impacted_files against the regulatory_model
2. THE Impact_Agent SHALL generate an impact_analysis containing: file_path, impact_type, severity, and description for each impacted file
3. THE Impact_Agent SHALL classify impact_type as "schema_change", "business_logic", "validation", or "api_contract"
4. THE Impact_Agent SHALL assign severity as "low", "medium", or "high" for each impact
5. THE Impact_Agent SHALL update the Global_State with the complete impact_analysis

### Requirement 7: Spec Generator Agent Processing

**User Story:** Como gerente de projeto, eu quero uma especificação técnica estruturada, para que eu possa comunicar as mudanças necessárias à equipe.

#### Acceptance Criteria

1. WHEN the SpecGenerator_Agent receives the Global_State, THE SpecGenerator_Agent SHALL generate a technical_spec document
2. THE technical_spec SHALL include sections: overview, affected_components, required_changes, acceptance_criteria, and estimated_effort
3. THE technical_spec SHALL reference all files from the impact_analysis
4. THE technical_spec SHALL be formatted in Markdown
5. THE SpecGenerator_Agent SHALL update the Global_State with the technical_spec

### Requirement 8: Kiro Prompt Generator Agent Processing

**User Story:** Como desenvolvedor, eu quero um prompt determinístico para implementação, para que eu possa executar as mudanças de forma consistente.

#### Acceptance Criteria

1. WHEN the KiroPrompt_Agent receives the Global_State, THE KiroPrompt_Agent SHALL generate a kiro_prompt for development
2. THE kiro_prompt SHALL include: context, specific_instructions, file_modifications, and validation_steps
3. THE kiro_prompt SHALL reference the technical_spec and impact_analysis
4. THE kiro_prompt SHALL be formatted as executable instructions
5. THE KiroPrompt_Agent SHALL update the Global_State with the kiro_prompt

### Requirement 9: Results Visualization

**User Story:** Como usuário do sistema, eu quero visualizar os resultados em abas organizadas, para que eu possa navegar facilmente entre diferentes saídas.

#### Acceptance Criteria

1. THE Frontend SHALL display results in five tabs: "Modelo Regulatório Estruturado", "Impacto no Código", "Especificação Técnica", "Prompt Final para Desenvolvimento", and "Fluxo de Execução dos Agentes"
2. WHEN analysis completes, THE Frontend SHALL populate tab 1 with the regulatory_model in formatted JSON
3. WHEN analysis completes, THE Frontend SHALL populate tab 2 with the impact_analysis in readable format
4. WHEN analysis completes, THE Frontend SHALL populate tab 3 with the technical_spec in Markdown
5. WHEN analysis completes, THE Frontend SHALL populate tab 4 with the kiro_prompt as text
6. WHEN analysis completes, THE Frontend SHALL populate tab 5 with the graph visualization

### Requirement 10: Graph Visualization

**User Story:** Como arquiteto de sistema, eu quero visualizar o fluxo de execução dos agentes, para que eu possa compreender a arquitetura multi-agente.

#### Acceptance Criteria

1. THE Graph_Visualizer SHALL generate a Mermaid diagram representing the agent execution flow
2. THE Mermaid diagram SHALL show nodes for: Sentinel_Agent, Translator_Agent, CodeReader_Agent, Impact_Agent, SpecGenerator_Agent, and KiroPrompt_Agent
3. THE Mermaid diagram SHALL show directed edges connecting agents in execution order
4. THE Frontend SHALL render the Mermaid diagram in tab 5
5. WHERE Graphviz is available, THE Graph_Visualizer SHALL provide an option to export the graph as PNG

### Requirement 11: Vector Store Management

**User Story:** Como administrador do sistema, eu quero armazenar embeddings do código, para que buscas semânticas sejam eficientes.

#### Acceptance Criteria

1. THE Vector_Store SHALL store embeddings of all files in the Pix_Repository
2. THE Vector_Store SHALL use PostgreSQL with pgvector extension
3. THE Vector_Store SHALL provide a table named embeddings with columns: id, file_path, content, embedding, and created_at
4. WHEN a file is added to Pix_Repository, THE System SHALL generate and store its embedding in the Vector_Store
5. THE Vector_Store SHALL support cosine similarity search for semantic matching

### Requirement 12: Audit Logging

**User Story:** Como auditor, eu quero logs persistentes de todas as execuções, para que eu possa rastrear análises realizadas.

#### Acceptance Criteria

1. THE System SHALL create an Audit_Log entry for each analysis execution
2. THE Audit_Log SHALL store: raw_regulatory_text, regulatory_model, impacted_files, impact_analysis, technical_spec, kiro_prompt, and execution_timestamp
3. THE Backend SHALL persist Audit_Log entries in a PostgreSQL table named audit_logs
4. THE audit_logs table SHALL include columns: id, raw_text, structured_model, impacted_files, impact_analysis, technical_spec, kiro_prompt, and timestamp
5. THE System SHALL complete audit logging within 2 seconds of analysis completion

### Requirement 13: Fake Pix Repository

**User Story:** Como desenvolvedor do sistema, eu quero um repositório fake de serviço Pix, para que eu possa testar a análise de impacto sem código real.

#### Acceptance Criteria

1. THE Pix_Repository SHALL contain a minimal functional Pix service implementation
2. THE Pix_Repository SHALL include an endpoint for Pix creation
3. THE Pix_Repository SHALL include a JSON schema definition for Pix transactions
4. THE Pix_Repository SHALL include a domain model representing Pix entities
5. THE Pix_Repository SHALL include at least one basic test file

### Requirement 14: Docker Deployment

**User Story:** Como operador do sistema, eu quero executar toda a aplicação via Docker, para que o ambiente seja consistente e reproduzível.

#### Acceptance Criteria

1. THE System SHALL provide a docker-compose.yml file that orchestrates all services
2. WHEN the command "docker-compose up --build" is executed, THE System SHALL start Frontend, Backend, and PostgreSQL services
3. THE Frontend SHALL be accessible at http://localhost:8501 after startup
4. THE Backend SHALL be accessible at http://localhost:8000 after startup
5. THE PostgreSQL service SHALL initialize with pgvector extension enabled

### Requirement 15: Global State Management

**User Story:** Como desenvolvedor do sistema, eu quero um estado global compartilhado, para que todos os agentes possam acessar e atualizar informações.

#### Acceptance Criteria

1. THE Global_State SHALL contain fields: raw_regulatory_text, change_detected, risk_level, regulatory_model, impacted_files, impact_analysis, technical_spec, kiro_prompt, and execution_timestamp
2. THE Global_State SHALL be implemented as a typed Python dataclass or Pydantic model
3. WHEN an agent updates the Global_State, THE LangGraph_Orchestrator SHALL validate the state structure
4. THE Global_State SHALL be serializable to JSON for storage in Audit_Log
5. THE Global_State SHALL be initialized with default values before the first agent executes

### Requirement 16: Local Execution

**User Story:** Como usuário do sistema, eu quero executar tudo localmente sem serviços pagos, para que eu possa usar o sistema sem custos externos.

#### Acceptance Criteria

1. THE System SHALL use only local LLM models or free API alternatives
2. THE System SHALL NOT require LangSmith or other paid monitoring services
3. THE System SHALL NOT require external API keys for BACEN or other regulatory sources
4. THE System SHALL generate embeddings using local models or free alternatives
5. THE System SHALL complete all operations without internet connectivity after initial setup
