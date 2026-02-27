# Design Document: Regulatory AI POC

## Overview

The regulatory-ai-poc is a multi-agent system that analyzes regulatory text, identifies impacts on a Pix service codebase, and generates technical specifications and development prompts. The system uses LangGraph for deterministic agent orchestration, operates entirely locally, and provides a web interface for interaction and visualization.

### Key Design Principles

- **Deterministic Orchestration**: LangGraph ensures predictable, sequential agent execution
- **Local-First**: All processing occurs locally without external API dependencies
- **Auditability**: Complete execution logs stored in PostgreSQL for compliance tracking
- **Semantic Search**: pgvector enables efficient code similarity matching
- **Modular Architecture**: Six specialized agents with clear responsibilities

### Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: FastAPI (async Python web framework)
- **Orchestration**: LangGraph (deterministic agent workflow)
- **Database**: PostgreSQL with pgvector extension
- **LLM**: Local models or free alternatives (no paid APIs)
- **Deployment**: Docker Compose
- **Visualization**: Mermaid diagrams

## Architecture

### High-Level System Architecture


```mermaid
graph TB
    User[User] -->|Input Text| Frontend[Streamlit Frontend]
    Frontend -->|POST /analyze| Backend[FastAPI Backend]
    Backend -->|Orchestrate| LangGraph[LangGraph Orchestrator]
    
    LangGraph -->|1| Sentinel[Sentinel Agent]
    LangGraph -->|2| Translator[Translator Agent]
    LangGraph -->|3| CodeReader[CodeReader Agent]
    LangGraph -->|4| Impact[Impact Agent]
    LangGraph -->|5| SpecGen[SpecGenerator Agent]
    LangGraph -->|6| KiroPrompt[KiroPrompt Agent]
    
    CodeReader -->|Query| VectorStore[(PostgreSQL + pgvector)]
    VectorStore -->|Embeddings| PixRepo[Fake Pix Repository]
    
    Backend -->|Store| AuditLog[(Audit Logs)]
    Backend -->|Results| Frontend
    Frontend -->|Display| Tabs[5 Result Tabs]
```

### Component Interaction Flow

1. User enters regulatory text in Streamlit frontend
2. Frontend sends POST request to FastAPI backend `/analyze` endpoint
3. Backend initializes Global State and invokes LangGraph orchestrator
4. LangGraph executes agents sequentially, each updating Global State:
   - Sentinel: Detects changes and assesses risk
   - Translator: Structures text into formal model
   - CodeReader: Queries vector store for relevant files
   - Impact: Analyzes technical impacts
   - SpecGenerator: Creates technical specification
   - KiroPrompt: Generates development prompt
5. Backend stores complete execution in audit log
6. Backend returns results to frontend
7. Frontend displays results across 5 tabs with graph visualization



## Components and Interfaces

### 1. Streamlit Frontend

**Responsibility**: Provide web interface for regulatory text input and results visualization

**Key Components**:
- Text input area for regulatory text
- "Analisar Impacto" button to trigger analysis
- Loading indicator during processing
- 5-tab result display interface
- Mermaid diagram renderer

**Interface**:
```python
class StreamlitApp:
    def render_input_section() -> None:
        """Render text area and submit button"""
        
    def validate_input(text: str) -> bool:
        """Validate non-empty text input"""
        
    def submit_analysis(text: str) -> dict:
        """POST to backend /analyze endpoint"""
        
    def render_results_tabs(results: dict) -> None:
        """Display 5 tabs with formatted results"""
        
    def render_mermaid_diagram(graph_data: str) -> None:
        """Render Mermaid visualization in tab 5"""
```

**Tab Structure**:
1. **Modelo Regulatório Estruturado**: JSON formatted regulatory model
2. **Impacto no Código**: Table/list of impacted files with severity
3. **Especificação Técnica**: Markdown rendered technical spec
4. **Prompt Final para Desenvolvimento**: Text display of Kiro prompt
5. **Fluxo de Execução dos Agentes**: Mermaid diagram of agent flow



### 2. FastAPI Backend

**Responsibility**: Expose REST API, orchestrate agent execution, manage persistence

**Key Endpoints**:

```python
@app.post("/analyze")
async def analyze_regulatory_text(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Main endpoint for regulatory text analysis
    
    Request:
        - regulatory_text: str
        
    Response:
        - regulatory_model: dict
        - impacted_files: list[dict]
        - impact_analysis: list[dict]
        - technical_spec: str
        - kiro_prompt: str
        - graph_visualization: str
        - execution_id: str
    """

@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""

@app.get("/audit/{execution_id}")
async def get_audit_log(execution_id: str) -> dict:
    """Retrieve specific audit log entry"""
```

**Core Services**:
```python
class OrchestrationService:
    def execute_analysis(text: str) -> GlobalState:
        """Initialize state and invoke LangGraph orchestrator"""
        
class AuditService:
    def save_execution(state: GlobalState) -> str:
        """Persist execution to audit_logs table"""
        
    def retrieve_execution(execution_id: str) -> GlobalState:
        """Load execution from audit_logs"""
```



### 3. LangGraph Orchestrator

**Responsibility**: Manage deterministic sequential execution of agents

**Architecture**:
```python
from langgraph.graph import StateGraph, END

class RegulatoryAnalysisGraph:
    def __init__(self):
        self.graph = StateGraph(GlobalState)
        self._build_graph()
        
    def _build_graph(self):
        """Define agent execution sequence"""
        self.graph.add_node("sentinel", sentinel_agent)
        self.graph.add_node("translator", translator_agent)
        self.graph.add_node("code_reader", code_reader_agent)
        self.graph.add_node("impact", impact_agent)
        self.graph.add_node("spec_generator", spec_generator_agent)
        self.graph.add_node("kiro_prompt", kiro_prompt_agent)
        
        # Define deterministic edges
        self.graph.set_entry_point("sentinel")
        self.graph.add_edge("sentinel", "translator")
        self.graph.add_edge("translator", "code_reader")
        self.graph.add_edge("code_reader", "impact")
        self.graph.add_edge("impact", "spec_generator")
        self.graph.add_edge("spec_generator", "kiro_prompt")
        self.graph.add_edge("kiro_prompt", END)
        
    def execute(self, initial_state: GlobalState) -> GlobalState:
        """Execute graph and return final state"""
        compiled = self.graph.compile()
        return compiled.invoke(initial_state)
```

**Error Handling**:
- Each agent wrapped in try-except block
- Failures logged with agent name and error details
- Execution halts on agent failure, partial state returned
- Error information added to Global State for debugging



### 4. Sentinel Agent

**Responsibility**: Detect regulatory changes and assess risk level

**Interface**:
```python
def sentinel_agent(state: GlobalState) -> GlobalState:
    """
    Analyze regulatory text for changes and risk
    
    Input: state.raw_regulatory_text
    Output: Updates state.change_detected, state.risk_level
    """
```

**Processing Logic**:
1. Parse regulatory text using local LLM
2. Identify keywords indicating changes: "alteração", "nova regra", "obrigatório"
3. Classify risk based on urgency and scope:
   - **High**: Mandatory changes with near deadlines
   - **Medium**: Recommended changes or moderate deadlines
   - **Low**: Informational or distant deadlines
4. Set `change_detected` to True if changes identified
5. Update Global State with results

**Performance**: Must complete within 10 seconds for texts up to 10,000 characters



### 5. Translator Agent

**Responsibility**: Structure regulatory text into formal model

**Interface**:
```python
def translator_agent(state: GlobalState) -> GlobalState:
    """
    Extract structured information from regulatory text
    
    Input: state.raw_regulatory_text
    Output: Updates state.regulatory_model
    """
```

**Regulatory Model Schema**:
```python
class RegulatoryModel(BaseModel):
    title: str
    description: str
    requirements: list[str]
    deadlines: list[dict[str, str]]  # [{"date": "2024-12-31", "description": "..."}]
    affected_systems: list[str]
```

**Processing Logic**:
1. Use local LLM to extract structured fields from text
2. Identify requirements as actionable items
3. Parse dates and associate with requirement descriptions
4. Identify system names (e.g., "Pix", "pagamentos", "transferências")
5. Validate JSON structure before updating state
6. Ensure round-trip serialization: `parse(format(model)) == model`



### 6. CodeReader Agent

**Responsibility**: Identify relevant code files using semantic search

**Interface**:
```python
def code_reader_agent(state: GlobalState) -> GlobalState:
    """
    Query vector store for relevant code files
    
    Input: state.regulatory_model
    Output: Updates state.impacted_files
    """
```

**Impacted File Schema**:
```python
class ImpactedFile(BaseModel):
    file_path: str
    relevance_score: float  # 0.0 to 1.0
    snippet: str  # First 200 chars of file
```

**Processing Logic**:
1. Generate search query from regulatory_model (combine title, requirements, affected_systems)
2. Create embedding for search query using local model
3. Query vector store with cosine similarity
4. Retrieve top 10 results ordered by relevance
5. If no results above threshold (0.5), return empty list
6. Update Global State with impacted_files list

**Vector Store Integration**:
```python
class VectorStoreClient:
    def search_similar(query_embedding: list[float], top_k: int = 10) -> list[ImpactedFile]:
        """Execute cosine similarity search"""
```



### 7. Impact Agent

**Responsibility**: Analyze technical impacts on identified code files

**Interface**:
```python
def impact_agent(state: GlobalState) -> GlobalState:
    """
    Analyze impacts for each identified file
    
    Input: state.regulatory_model, state.impacted_files
    Output: Updates state.impact_analysis
    """
```

**Impact Analysis Schema**:
```python
class Impact(BaseModel):
    file_path: str
    impact_type: Literal["schema_change", "business_logic", "validation", "api_contract"]
    severity: Literal["low", "medium", "high"]
    description: str
    suggested_changes: list[str]
```

**Processing Logic**:
1. For each file in impacted_files:
   - Load file content from Pix repository
   - Analyze against regulatory requirements using LLM
   - Classify impact type based on file content:
     - **schema_change**: Database models, migrations
     - **business_logic**: Service layer, domain logic
     - **validation**: Input validators, business rules
     - **api_contract**: API endpoints, request/response models
   - Assess severity based on scope and complexity
   - Generate description and suggested changes
2. Compile all impacts into list
3. Update Global State with impact_analysis



### 8. SpecGenerator Agent

**Responsibility**: Generate structured technical specification document

**Interface**:
```python
def spec_generator_agent(state: GlobalState) -> GlobalState:
    """
    Create technical specification from analysis
    
    Input: state.regulatory_model, state.impact_analysis
    Output: Updates state.technical_spec
    """
```

**Technical Spec Structure** (Markdown):
```markdown
# Technical Specification: [Regulatory Title]

## Overview
[Description from regulatory_model]

## Affected Components
- [List of impacted files with impact types]

## Required Changes
### [File Path 1]
- Impact Type: [type]
- Severity: [severity]
- Changes:
  - [Suggested change 1]
  - [Suggested change 2]

## Acceptance Criteria
- [Derived from regulatory requirements]

## Estimated Effort
- [Calculated based on number and severity of impacts]
```

**Processing Logic**:
1. Generate overview from regulatory_model
2. List all impacted files grouped by impact_type
3. Detail required changes for each file
4. Convert regulatory requirements to acceptance criteria
5. Estimate effort: sum(severity_weights) where high=3, medium=2, low=1
6. Format as Markdown string
7. Update Global State with technical_spec



### 9. KiroPrompt Agent

**Responsibility**: Generate deterministic development prompt

**Interface**:
```python
def kiro_prompt_agent(state: GlobalState) -> GlobalState:
    """
    Create executable development prompt
    
    Input: state.technical_spec, state.impact_analysis
    Output: Updates state.kiro_prompt
    """
```

**Kiro Prompt Structure**:
```
CONTEXT:
[Regulatory requirement summary]

OBJECTIVE:
Implement changes to comply with [regulatory title]

SPECIFIC INSTRUCTIONS:
1. [Step-by-step instructions derived from impact_analysis]

FILE MODIFICATIONS:
- [file_path]: [specific changes needed]

VALIDATION STEPS:
1. [Test criteria from acceptance criteria]
2. Verify compliance with regulatory requirements
3. Run existing test suite

CONSTRAINTS:
- Maintain backward compatibility where possible
- Follow existing code patterns
- Update documentation
```

**Processing Logic**:
1. Extract context from regulatory_model
2. Generate step-by-step instructions from impact_analysis
3. List file modifications with specific changes
4. Create validation steps from technical_spec acceptance criteria
5. Add standard constraints
6. Format as plain text prompt
7. Update Global State with kiro_prompt



### 10. Graph Visualizer

**Responsibility**: Generate visual representation of agent execution flow

**Interface**:
```python
class GraphVisualizer:
    def generate_mermaid_diagram(state: GlobalState) -> str:
        """Generate Mermaid diagram showing agent flow"""
        
    def export_png(mermaid_str: str) -> bytes:
        """Export diagram as PNG if Graphviz available"""
```

**Mermaid Diagram Template**:
```mermaid
graph LR
    Start([Input Text]) --> Sentinel[Sentinel Agent<br/>Change: {change_detected}<br/>Risk: {risk_level}]
    Sentinel --> Translator[Translator Agent<br/>Model Created]
    Translator --> CodeReader[CodeReader Agent<br/>{n} Files Found]
    CodeReader --> Impact[Impact Agent<br/>{n} Impacts Identified]
    Impact --> SpecGen[SpecGenerator Agent<br/>Spec Created]
    SpecGen --> KiroPrompt[KiroPrompt Agent<br/>Prompt Generated]
    KiroPrompt --> End([Complete])
```

**Processing Logic**:
1. Build Mermaid syntax string with agent nodes
2. Annotate each node with key outputs from Global State
3. Add directed edges showing execution sequence
4. Return formatted Mermaid string for frontend rendering
5. Optionally convert to PNG using Graphviz if available



## Data Models

### Global State

The Global State is the central data structure passed between all agents, containing all inputs, intermediate results, and final outputs.

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class GlobalState(BaseModel):
    """Shared state object passed through agent pipeline"""
    
    # Input
    raw_regulatory_text: str = Field(description="Original regulatory text input")
    
    # Sentinel outputs
    change_detected: Optional[bool] = Field(default=None, description="Whether regulatory changes detected")
    risk_level: Optional[str] = Field(default=None, description="Risk level: low, medium, high")
    
    # Translator outputs
    regulatory_model: Optional[dict] = Field(default=None, description="Structured regulatory model")
    
    # CodeReader outputs
    impacted_files: list[dict] = Field(default_factory=list, description="List of relevant code files")
    
    # Impact outputs
    impact_analysis: list[dict] = Field(default_factory=list, description="Detailed impact analysis")
    
    # SpecGenerator outputs
    technical_spec: Optional[str] = Field(default=None, description="Markdown technical specification")
    
    # KiroPrompt outputs
    kiro_prompt: Optional[str] = Field(default=None, description="Development prompt")
    
    # Metadata
    execution_timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_id: Optional[str] = Field(default=None, description="Unique execution identifier")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```



### Regulatory Model

Structured representation of regulatory text extracted by Translator Agent.

```python
class RegulatoryModel(BaseModel):
    """Formal structure of regulatory requirements"""
    
    title: str = Field(description="Regulatory change title")
    description: str = Field(description="Detailed description of the regulation")
    requirements: list[str] = Field(description="List of specific requirements")
    deadlines: list[dict[str, str]] = Field(
        description="Deadlines with date and description",
        example=[{"date": "2024-12-31", "description": "Implementation deadline"}]
    )
    affected_systems: list[str] = Field(description="Systems impacted by regulation")
```

### Impacted File

Represents a code file identified as relevant by CodeReader Agent.

```python
class ImpactedFile(BaseModel):
    """Code file with relevance to regulatory change"""
    
    file_path: str = Field(description="Relative path to file in repository")
    relevance_score: float = Field(ge=0.0, le=1.0, description="Cosine similarity score")
    snippet: str = Field(description="First 200 characters of file content")
```

### Impact Analysis

Detailed analysis of how a regulatory change affects a specific file.

```python
class Impact(BaseModel):
    """Technical impact on a specific file"""
    
    file_path: str = Field(description="Path to impacted file")
    impact_type: Literal["schema_change", "business_logic", "validation", "api_contract"]
    severity: Literal["low", "medium", "high"]
    description: str = Field(description="Explanation of the impact")
    suggested_changes: list[str] = Field(description="Recommended code modifications")
```



## Database Schema

### PostgreSQL with pgvector

The system uses PostgreSQL with the pgvector extension for storing embeddings and audit logs.

**Database Name**: `regulatory_ai`

### Embeddings Table

Stores vector embeddings of code files for semantic search.

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(512) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    embedding vector(384),  -- Dimension depends on embedding model
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Columns**:
- `id`: Auto-incrementing primary key
- `file_path`: Unique path to file in repository
- `content`: Full text content of the file
- `embedding`: Vector representation (384 dimensions for sentence-transformers/all-MiniLM-L6-v2)
- `created_at`: Timestamp of initial embedding creation
- `updated_at`: Timestamp of last embedding update

**Indexes**:
- IVFFlat index on embedding column for fast cosine similarity search



### Audit Logs Table

Stores complete execution history for compliance and debugging.

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL UNIQUE,
    raw_text TEXT NOT NULL,
    change_detected BOOLEAN,
    risk_level VARCHAR(10),
    structured_model JSONB,
    impacted_files JSONB,
    impact_analysis JSONB,
    technical_spec TEXT,
    kiro_prompt TEXT,
    error TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_risk_level ON audit_logs(risk_level);
```

**Columns**:
- `id`: Auto-incrementing primary key
- `execution_id`: UUID for unique execution identification
- `raw_text`: Original regulatory text input
- `change_detected`: Boolean from Sentinel Agent
- `risk_level`: Risk assessment (low/medium/high)
- `structured_model`: JSON of RegulatoryModel
- `impacted_files`: JSON array of ImpactedFile objects
- `impact_analysis`: JSON array of Impact objects
- `technical_spec`: Markdown technical specification
- `kiro_prompt`: Generated development prompt
- `error`: Error message if execution failed
- `timestamp`: Execution timestamp

**Indexes**:
- Timestamp index for chronological queries
- Risk level index for filtering by severity



## API Design

### FastAPI Endpoints

#### POST /analyze

Analyzes regulatory text and returns complete results.

**Request**:
```json
{
  "regulatory_text": "string"
}
```

**Response** (200 OK):
```json
{
  "execution_id": "uuid-string",
  "change_detected": true,
  "risk_level": "high",
  "regulatory_model": {
    "title": "string",
    "description": "string",
    "requirements": ["string"],
    "deadlines": [{"date": "2024-12-31", "description": "string"}],
    "affected_systems": ["string"]
  },
  "impacted_files": [
    {
      "file_path": "string",
      "relevance_score": 0.85,
      "snippet": "string"
    }
  ],
  "impact_analysis": [
    {
      "file_path": "string",
      "impact_type": "business_logic",
      "severity": "high",
      "description": "string",
      "suggested_changes": ["string"]
    }
  ],
  "technical_spec": "markdown string",
  "kiro_prompt": "string",
  "graph_visualization": "mermaid string",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Regulatory text cannot be empty"
}
```

**Error Response** (500 Internal Server Error):
```json
{
  "detail": "Agent execution failed: [error details]",
  "execution_id": "uuid-string"
}
```



#### GET /health

Health check endpoint for monitoring.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "database": "connected",
  "vector_store": "ready",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### GET /audit/{execution_id}

Retrieves a specific audit log entry.

**Response** (200 OK):
```json
{
  "execution_id": "uuid-string",
  "raw_text": "string",
  "change_detected": true,
  "risk_level": "high",
  "structured_model": {},
  "impacted_files": [],
  "impact_analysis": [],
  "technical_spec": "string",
  "kiro_prompt": "string",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Execution not found"
}
```



## Frontend Design

### Streamlit Interface Structure

The frontend is a single-page Streamlit application with two main sections: input and results.

#### Input Section

```python
import streamlit as st

st.title("Análise de Impacto Regulatório - POC")

# Text input
regulatory_text = st.text_area(
    "Texto Regulatório",
    height=200,
    placeholder="Cole aqui o texto regulatório para análise..."
)

# Submit button
if st.button("Analisar Impacto", type="primary"):
    if not regulatory_text.strip():
        st.error("Por favor, insira um texto regulatório.")
    else:
        with st.spinner("Analisando... Isso pode levar alguns segundos."):
            # Call backend API
            results = analyze_text(regulatory_text)
            st.session_state['results'] = results
```

#### Results Section (5 Tabs)

```python
if 'results' in st.session_state:
    results = st.session_state['results']
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Modelo Regulatório Estruturado",
        "💻 Impacto no Código",
        "📝 Especificação Técnica",
        "🚀 Prompt Final para Desenvolvimento",
        "🔄 Fluxo de Execução dos Agentes"
    ])
    
    with tab1:
        st.json(results['regulatory_model'])
    
    with tab2:
        for impact in results['impact_analysis']:
            with st.expander(f"{impact['file_path']} - {impact['severity'].upper()}"):
                st.write(f"**Tipo:** {impact['impact_type']}")
                st.write(f"**Descrição:** {impact['description']}")
                st.write("**Mudanças Sugeridas:**")
                for change in impact['suggested_changes']:
                    st.write(f"- {change}")
    
    with tab3:
        st.markdown(results['technical_spec'])
    
    with tab4:
        st.text(results['kiro_prompt'])
    
    with tab5:
        st.write("### Fluxo de Execução dos Agentes")
        st.write(f"**ID da Execução:** {results['execution_id']}")
        st.write(f"**Timestamp:** {results['timestamp']}")
        
        # Render Mermaid diagram
        import streamlit.components.v1 as components
        mermaid_html = f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>mermaid.initialize({{startOnLoad:true}});</script>
        <div class="mermaid">
        {results['graph_visualization']}
        </div>
        """
        components.html(mermaid_html, height=400)
```



## Docker Deployment Architecture

### Docker Compose Configuration

The system uses Docker Compose to orchestrate three services: frontend, backend, and database.

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: regulatory_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/regulatory_ai
      PIX_REPO_PATH: /app/fake_pix_repo
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./fake_pix_repo:/app/fake_pix_repo

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    environment:
      BACKEND_URL: http://backend:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```



### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Database Initialization Script

```sql
-- init.sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(512) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL UNIQUE,
    raw_text TEXT NOT NULL,
    change_detected BOOLEAN,
    risk_level VARCHAR(10),
    structured_model JSONB,
    impacted_files JSONB,
    impact_analysis JSONB,
    technical_spec TEXT,
    kiro_prompt TEXT,
    error TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_risk_level ON audit_logs(risk_level);
```



## Integration Patterns

### Frontend-Backend Communication

**Pattern**: REST API with JSON payloads

```python
# Frontend (Streamlit)
import requests

def analyze_text(regulatory_text: str) -> dict:
    """Call backend API to analyze regulatory text"""
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    response = requests.post(
        f"{backend_url}/analyze",
        json={"regulatory_text": regulatory_text},
        timeout=120  # 2 minutes for long-running analysis
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Analysis failed: {response.json()['detail']}")
```

### Backend-Database Communication

**Pattern**: SQLAlchemy ORM with async support

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Database connection
engine = create_async_engine(
    os.getenv("DATABASE_URL"),
    echo=False,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Usage in endpoints
async def save_audit_log(state: GlobalState):
    async with AsyncSessionLocal() as session:
        audit_entry = AuditLog(
            execution_id=state.execution_id,
            raw_text=state.raw_regulatory_text,
            change_detected=state.change_detected,
            risk_level=state.risk_level,
            structured_model=state.regulatory_model,
            impacted_files=state.impacted_files,
            impact_analysis=state.impact_analysis,
            technical_spec=state.technical_spec,
            kiro_prompt=state.kiro_prompt,
            timestamp=state.execution_timestamp
        )
        session.add(audit_entry)
        await session.commit()
```



### Agent-Vector Store Communication

**Pattern**: Direct SQL queries with pgvector operators

```python
from pgvector.sqlalchemy import Vector
from sqlalchemy import select, func

class VectorStoreService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def search_similar(
        self, 
        query_embedding: list[float], 
        top_k: int = 10,
        threshold: float = 0.5
    ) -> list[ImpactedFile]:
        """Search for similar code files using cosine similarity"""
        
        # Query using pgvector cosine distance operator
        stmt = (
            select(
                Embedding.file_path,
                Embedding.content,
                (1 - Embedding.embedding.cosine_distance(query_embedding)).label('score')
            )
            .where((1 - Embedding.embedding.cosine_distance(query_embedding)) >= threshold)
            .order_by((1 - Embedding.embedding.cosine_distance(query_embedding)).desc())
            .limit(top_k)
        )
        
        result = await self.session.execute(stmt)
        rows = result.all()
        
        return [
            ImpactedFile(
                file_path=row.file_path,
                relevance_score=row.score,
                snippet=row.content[:200]
            )
            for row in rows
        ]
    
    async def upsert_embedding(
        self, 
        file_path: str, 
        content: str, 
        embedding: list[float]
    ):
        """Insert or update file embedding"""
        stmt = (
            insert(Embedding)
            .values(
                file_path=file_path,
                content=content,
                embedding=embedding
            )
            .on_conflict_do_update(
                index_elements=['file_path'],
                set_={
                    'content': content,
                    'embedding': embedding,
                    'updated_at': func.now()
                }
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()
```



### LLM Integration Pattern

**Pattern**: Local model with fallback to free API

```python
from typing import Protocol

class LLMProvider(Protocol):
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text from prompt"""
        ...

class LocalLLM:
    """Local LLM using transformers or llama.cpp"""
    
    def __init__(self, model_path: str):
        # Load local model (e.g., Llama 2, Mistral)
        self.model = self._load_model(model_path)
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        return self.model.generate(prompt, max_tokens=max_tokens)

class OllamaLLM:
    """Ollama API for local models"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"]

# Factory pattern for LLM selection
def get_llm() -> LLMProvider:
    llm_type = os.getenv("LLM_TYPE", "ollama")
    
    if llm_type == "ollama":
        return OllamaLLM()
    elif llm_type == "local":
        return LocalLLM(os.getenv("MODEL_PATH"))
    else:
        raise ValueError(f"Unknown LLM type: {llm_type}")
```



### Embedding Generation Pattern

**Pattern**: Local sentence-transformers model

```python
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    """Generate embeddings using local model"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def encode(self, text: str) -> list[float]:
        """Generate embedding for text"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

# Initialize embeddings for Pix repository
async def initialize_vector_store(repo_path: str, vector_store: VectorStoreService):
    """Generate and store embeddings for all files in repository"""
    embedding_service = EmbeddingService()
    
    for file_path in Path(repo_path).rglob("*.py"):
        content = file_path.read_text()
        embedding = embedding_service.encode(content)
        
        await vector_store.upsert_embedding(
            file_path=str(file_path.relative_to(repo_path)),
            content=content,
            embedding=embedding
        )
```



## Fake Pix Repository Structure

The fake Pix repository simulates a minimal Pix service implementation for testing impact analysis.

```
fake_pix_repo/
├── api/
│   ├── __init__.py
│   ├── endpoints.py          # FastAPI endpoints for Pix operations
│   └── schemas.py            # Pydantic request/response models
├── domain/
│   ├── __init__.py
│   ├── models.py             # Domain entities (Pix, Account, Transaction)
│   └── validators.py         # Business rule validators
├── services/
│   ├── __init__.py
│   ├── pix_service.py        # Business logic for Pix operations
│   └── notification_service.py
├── database/
│   ├── __init__.py
│   ├── models.py             # SQLAlchemy ORM models
│   └── migrations/
│       └── 001_initial.sql
├── tests/
│   ├── __init__.py
│   ├── test_pix_creation.py
│   └── test_validators.py
└── README.md
```

**Key Files Content**:

`api/endpoints.py`:
```python
from fastapi import APIRouter, HTTPException
from .schemas import PixCreateRequest, PixResponse

router = APIRouter()

@router.post("/pix", response_model=PixResponse)
async def create_pix(request: PixCreateRequest):
    """Create a new Pix transaction"""
    # Implementation
    pass
```

`domain/models.py`:
```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Pix:
    id: str
    sender_key: str
    receiver_key: str
    amount: Decimal
    description: str
```

`database/models.py`:
```python
from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PixTransaction(Base):
    __tablename__ = "pix_transactions"
    
    id = Column(String, primary_key=True)
    sender_key = Column(String, nullable=False)
    receiver_key = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, nullable=False)
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, several redundancies were identified:
- Criteria 2.3 is subsumed by 2.1 (deterministic sequence implies automatic triggering)
- Criteria 3.4, 4.3, 6.5, 7.5, 8.5 are redundant with their respective field-setting criteria
- Criteria 10.4 is redundant with 9.6 (both test graph rendering in tab 5)
- Many "SHALL update Global_State" criteria are redundant with testing that specific fields are populated

The following properties focus on unique, testable behaviors that provide validation value.



### Property 1: Frontend API Call on Submit

*For any* non-empty regulatory text input, when the user clicks "Analisar Impacto", the frontend should send a POST request to the backend /analyze endpoint with the text as payload.

**Validates: Requirements 1.3**

### Property 2: Deterministic Agent Execution Sequence

*For any* regulatory text input, the LangGraph orchestrator should execute agents in the fixed sequence: Sentinel → Translator → CodeReader → Impact → SpecGenerator → KiroPrompt, with no agents skipped or reordered.

**Validates: Requirements 2.1**

### Property 3: State Propagation Between Agents

*For any* execution, each agent in the pipeline should receive the Global State that was modified by the previous agent, ensuring state continuity.

**Validates: Requirements 2.2**

### Property 4: State Mutation After Agent Execution

*For any* agent execution, the Global State should be modified (at least one field updated) after the agent completes, demonstrating that the agent performed its work.

**Validates: Requirements 2.4**

### Property 5: Error Handling Halts Execution

*For any* agent that raises an exception, the orchestrator should log the error, halt further agent execution, and return the partial state with error information populated.

**Validates: Requirements 2.5**

### Property 6: Sentinel Sets Change Detection

*For any* regulatory text input, after Sentinel Agent execution, the Global State should have change_detected set to either True or False (not None).

**Validates: Requirements 3.2**

### Property 7: Sentinel Sets Valid Risk Level

*For any* regulatory text input, after Sentinel Agent execution, the Global State should have risk_level set to one of: "low", "medium", or "high".

**Validates: Requirements 3.3**



### Property 8: Regulatory Model Has Required Fields

*For any* regulatory text input, after Translator Agent execution, the regulatory_model should contain all required fields: title, description, requirements, deadlines, and affected_systems.

**Validates: Requirements 4.2**

### Property 9: Regulatory Model JSON Validity

*For any* regulatory text input, the regulatory_model should be serializable to valid JSON and parseable back without errors.

**Validates: Requirements 4.4**

### Property 10: Regulatory Model Round-Trip Serialization

*For any* regulatory_model object, serializing to JSON then deserializing should produce an equivalent object with all fields preserved.

**Validates: Requirements 4.5**

### Property 11: CodeReader Returns At Most 10 Files

*For any* regulatory text input, after CodeReader Agent execution, the impacted_files list should contain at most 10 files.

**Validates: Requirements 5.2**

### Property 12: Impacted Files Have Required Structure

*For any* file in the impacted_files list, it should have a file_path (non-empty string) and a relevance_score (float between 0.0 and 1.0).

**Validates: Requirements 5.3**

### Property 13: Impact Analysis Has Required Fields

*For any* impact in the impact_analysis list, it should contain all required fields: file_path, impact_type, severity, description, and suggested_changes.

**Validates: Requirements 6.2**

### Property 14: Impact Type Is Valid

*For any* impact in the impact_analysis list, the impact_type should be one of: "schema_change", "business_logic", "validation", or "api_contract".

**Validates: Requirements 6.3**

### Property 15: Impact Severity Is Valid

*For any* impact in the impact_analysis list, the severity should be one of: "low", "medium", or "high".

**Validates: Requirements 6.4**



### Property 16: Technical Spec Is Generated

*For any* regulatory text input, after SpecGenerator Agent execution, the technical_spec should be a non-empty string.

**Validates: Requirements 7.1**

### Property 17: Technical Spec Contains Required Sections

*For any* generated technical_spec, it should contain markdown headers for all required sections: overview, affected_components, required_changes, acceptance_criteria, and estimated_effort.

**Validates: Requirements 7.2**

### Property 18: Technical Spec References All Impacted Files

*For any* execution, all file paths from the impact_analysis should appear somewhere in the technical_spec text.

**Validates: Requirements 7.3**

### Property 19: Technical Spec Is Valid Markdown

*For any* generated technical_spec, it should contain valid markdown syntax including headers (lines starting with #) and lists (lines starting with - or numbers).

**Validates: Requirements 7.4**

### Property 20: Kiro Prompt Is Generated

*For any* regulatory text input, after KiroPrompt Agent execution, the kiro_prompt should be a non-empty string.

**Validates: Requirements 8.1**

### Property 21: Kiro Prompt Contains Required Sections

*For any* generated kiro_prompt, it should contain all required sections: CONTEXT, OBJECTIVE, SPECIFIC INSTRUCTIONS, FILE MODIFICATIONS, VALIDATION STEPS, and CONSTRAINTS.

**Validates: Requirements 8.2**

### Property 22: Kiro Prompt References Source Data

*For any* execution, the kiro_prompt should reference data from both the technical_spec and impact_analysis (e.g., file paths, requirements, or changes mentioned).

**Validates: Requirements 8.3**



### Property 23: Frontend Displays Results in Correct Tabs

*For any* completed analysis, the frontend should populate tab 1 with regulatory_model JSON, tab 2 with impact_analysis, tab 3 with technical_spec markdown, tab 4 with kiro_prompt text, and tab 5 with graph visualization.

**Validates: Requirements 9.2, 9.3, 9.4, 9.5, 9.6**

### Property 24: Mermaid Diagram Is Generated

*For any* execution, the Graph_Visualizer should generate a non-empty Mermaid diagram string.

**Validates: Requirements 10.1**

### Property 25: Mermaid Diagram Contains All Agents

*For any* generated Mermaid diagram, it should contain node references for all six agents: Sentinel_Agent, Translator_Agent, CodeReader_Agent, Impact_Agent, SpecGenerator_Agent, and KiroPrompt_Agent.

**Validates: Requirements 10.2**

### Property 26: Mermaid Diagram Shows Execution Order

*For any* generated Mermaid diagram, it should contain directed edges connecting agents in the correct execution sequence (Sentinel → Translator → CodeReader → Impact → SpecGenerator → KiroPrompt).

**Validates: Requirements 10.3**

### Property 27: Graphviz Export When Available

*For any* execution where Graphviz is installed, the Graph_Visualizer should successfully export the Mermaid diagram to PNG format without errors.

**Validates: Requirements 10.5**

### Property 28: Vector Store Contains All Repository Files

*For any* initialized system, the number of embeddings in the Vector_Store should equal the number of Python files in the Pix_Repository.

**Validates: Requirements 11.1**

### Property 29: File Addition Creates Embedding

*For any* new file added to the Pix_Repository, the system should generate and store a corresponding embedding in the Vector_Store with matching file_path.

**Validates: Requirements 11.4**



### Property 30: Cosine Similarity Search Returns Ordered Results

*For any* search query, the Vector_Store should return results ordered by relevance_score in descending order (highest similarity first).

**Validates: Requirements 11.5**

### Property 31: Audit Log Created Per Execution

*For any* analysis execution, exactly one audit log entry should be created in the database with a unique execution_id.

**Validates: Requirements 12.1**

### Property 32: Audit Log Contains All Required Fields

*For any* audit log entry, it should contain all required fields: raw_regulatory_text, regulatory_model, impacted_files, impact_analysis, technical_spec, kiro_prompt, and execution_timestamp.

**Validates: Requirements 12.2**

### Property 33: Global State Validation

*For any* agent that updates the Global_State, if the update violates the state schema (e.g., wrong type, missing required field), the orchestrator should reject the update and raise a validation error.

**Validates: Requirements 15.3**

### Property 34: Global State Serialization Round-Trip

*For any* Global_State object, serializing to JSON then deserializing should produce an equivalent state with all fields preserved and correct types.

**Validates: Requirements 15.4**

### Property 35: Offline Operation After Setup

*For any* analysis execution after initial setup (embeddings generated, models downloaded), the system should complete successfully without any network requests to external services.

**Validates: Requirements 16.5**



## Error Handling

### Frontend Error Handling

**Input Validation**:
- Empty text input: Display error message "Por favor, insira um texto regulatório."
- Network errors: Display error message with retry option
- Timeout errors (>2 minutes): Display timeout message and suggest shorter text

**Error Display**:
```python
try:
    results = analyze_text(regulatory_text)
    st.session_state['results'] = results
except requests.Timeout:
    st.error("⏱️ A análise excedeu o tempo limite. Tente com um texto menor.")
except requests.RequestException as e:
    st.error(f"❌ Erro ao conectar com o backend: {str(e)}")
except Exception as e:
    st.error(f"❌ Erro inesperado: {str(e)}")
```

### Backend Error Handling

**API Endpoint Error Responses**:
- 400 Bad Request: Invalid input (empty text, malformed JSON)
- 500 Internal Server Error: Agent execution failure, database errors
- 503 Service Unavailable: Database connection failure

**Agent Execution Errors**:
```python
async def execute_analysis(text: str) -> GlobalState:
    state = GlobalState(raw_regulatory_text=text, execution_id=str(uuid.uuid4()))
    
    try:
        orchestrator = RegulatoryAnalysisGraph()
        final_state = orchestrator.execute(state)
        return final_state
    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}", exc_info=True)
        state.error = f"Execution failed at agent: {str(e)}"
        # Save partial state to audit log
        await save_audit_log(state)
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        )
```



### Agent-Level Error Handling

Each agent should implement try-except blocks with specific error handling:

```python
def sentinel_agent(state: GlobalState) -> GlobalState:
    try:
        # Agent logic
        llm = get_llm()
        analysis = llm.generate(f"Analyze regulatory text: {state.raw_regulatory_text}")
        
        state.change_detected = detect_changes(analysis)
        state.risk_level = assess_risk(analysis)
        
        return state
    except Exception as e:
        logger.error(f"Sentinel agent failed: {str(e)}")
        # Set default values to allow pipeline to continue if possible
        state.change_detected = False
        state.risk_level = "unknown"
        state.error = f"Sentinel: {str(e)}"
        raise  # Re-raise to halt execution
```

### Database Error Handling

**Connection Failures**:
- Retry logic with exponential backoff (3 attempts)
- Fallback to in-memory storage for non-critical operations
- Clear error messages for connection issues

**Query Failures**:
- Transaction rollback on errors
- Detailed logging of failed queries
- Graceful degradation (e.g., skip audit logging if database unavailable)

### LLM Error Handling

**Model Loading Failures**:
- Check model availability at startup
- Provide clear error messages if models not found
- Suggest model download commands

**Generation Failures**:
- Retry with reduced max_tokens
- Fallback to simpler prompts
- Log generation errors with context



## Testing Strategy

### Dual Testing Approach

The system requires both unit tests and property-based tests for comprehensive coverage:

- **Unit Tests**: Verify specific examples, edge cases, and integration points
- **Property Tests**: Verify universal properties across randomized inputs

Both testing approaches are complementary and necessary. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across a wide input space.

### Property-Based Testing Configuration

**Library Selection**: Use `hypothesis` for Python property-based testing

**Test Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: regulatory-ai-poc, Property {number}: {property_text}`

**Example Property Test**:
```python
from hypothesis import given, strategies as st

# Feature: regulatory-ai-poc, Property 10: Regulatory Model Round-Trip Serialization
@given(st.builds(RegulatoryModel))
def test_regulatory_model_round_trip(model):
    """For any regulatory_model, serialize then deserialize produces equivalent object"""
    json_str = model.model_dump_json()
    restored = RegulatoryModel.model_validate_json(json_str)
    assert restored == model
```



### Unit Testing Strategy

**Frontend Tests** (`frontend/tests/`):
- Test input validation (empty text rejection)
- Test API call construction
- Test tab rendering with mock data
- Test error message display

**Backend API Tests** (`backend/tests/test_api.py`):
- Test `/analyze` endpoint with valid input
- Test `/analyze` endpoint with empty input (400 error)
- Test `/health` endpoint
- Test `/audit/{execution_id}` endpoint with valid/invalid IDs

**Agent Tests** (`backend/tests/test_agents.py`):
- Test each agent with sample inputs
- Test agent state updates
- Test agent error handling
- Test agent output structure

**Orchestrator Tests** (`backend/tests/test_orchestrator.py`):
- Test deterministic execution sequence
- Test state propagation between agents
- Test error handling and execution halt
- Test partial state on failure

**Vector Store Tests** (`backend/tests/test_vector_store.py`):
- Test embedding storage and retrieval
- Test cosine similarity search
- Test result ordering by relevance
- Test empty result handling

**Database Tests** (`backend/tests/test_database.py`):
- Test audit log creation
- Test audit log retrieval
- Test schema validation
- Test connection error handling



### Property-Based Testing Strategy

**State Management Properties** (`backend/tests/property_tests/test_state_properties.py`):
- Property 10: Regulatory model round-trip serialization
- Property 34: Global state serialization round-trip
- Property 33: Global state validation rejects invalid updates

**Agent Pipeline Properties** (`backend/tests/property_tests/test_pipeline_properties.py`):
- Property 2: Deterministic agent execution sequence
- Property 3: State propagation between agents
- Property 4: State mutation after agent execution
- Property 5: Error handling halts execution

**Agent Output Properties** (`backend/tests/property_tests/test_agent_properties.py`):
- Property 6: Sentinel sets change detection
- Property 7: Sentinel sets valid risk level
- Property 8: Regulatory model has required fields
- Property 11: CodeReader returns at most 10 files
- Property 12: Impacted files have required structure
- Property 13-15: Impact analysis structure and valid values
- Property 16-19: Technical spec generation and structure
- Property 20-22: Kiro prompt generation and structure

**Vector Store Properties** (`backend/tests/property_tests/test_vector_properties.py`):
- Property 28: Vector store contains all repository files
- Property 29: File addition creates embedding
- Property 30: Cosine similarity returns ordered results

**Audit Properties** (`backend/tests/property_tests/test_audit_properties.py`):
- Property 31: Audit log created per execution
- Property 32: Audit log contains all required fields

**Integration Properties** (`backend/tests/property_tests/test_integration_properties.py`):
- Property 35: Offline operation after setup



### Edge Case Testing

**Edge Cases to Cover**:
- Empty regulatory text (validation error)
- Very long regulatory text (>10,000 characters)
- Regulatory text with no changes detected
- No relevant files found in vector search
- Agent execution timeout
- Database connection failure during execution
- Missing LLM model
- Malformed JSON in regulatory model
- Special characters in file paths
- Empty impact analysis
- Network disconnection during offline operation test

### Integration Testing

**End-to-End Tests** (`tests/integration/test_e2e.py`):
- Full pipeline execution with sample regulatory text
- Verify all agents execute in sequence
- Verify all outputs are generated
- Verify audit log is created
- Verify frontend can display results

**Docker Integration Tests** (`tests/integration/test_docker.py`):
- Test docker-compose startup
- Test service health checks
- Test inter-service communication
- Test database initialization
- Test volume persistence

### Test Data

**Sample Regulatory Texts** (`tests/fixtures/regulatory_texts.py`):
- Short regulation (100 words)
- Medium regulation (500 words)
- Long regulation (2000 words)
- Regulation with explicit deadlines
- Regulation mentioning Pix system
- Regulation with no changes (informational)

**Mock Responses** (`tests/fixtures/mock_responses.py`):
- Mock LLM responses for each agent
- Mock vector search results
- Mock database responses

