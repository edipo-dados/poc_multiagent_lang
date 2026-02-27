0]# Implementation Plan: Regulatory AI POC

## Overview

This implementation plan breaks down the regulatory-ai-poc multi-agent system into discrete coding tasks. The system uses LangGraph for deterministic agent orchestration, FastAPI for the backend, Streamlit for the frontend, and PostgreSQL with pgvector for semantic search. All components run locally via Docker Compose.

The implementation follows a bottom-up approach: infrastructure first, then data layer, then agents, then orchestration, and finally the frontend interface.

## Tasks

- [x] 1. Set up project structure and Docker infrastructure
  - Create directory structure for backend, frontend, and fake Pix repository
  - Write docker-compose.yml with PostgreSQL (pgvector), backend, and frontend services
  - Create Dockerfiles for backend and frontend
  - Write database initialization script (init.sql) with embeddings and audit_logs tables
  - Create requirements.txt files for backend and frontend
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 2. Create fake Pix repository
  - [x] 2.1 Implement Pix repository structure and domain models
    - Create directory structure: api/, domain/, services/, database/, tests/
    - Implement domain/models.py with Pix, Account, Transaction dataclasses
    - Implement database/models.py with SQLAlchemy ORM models
    - Implement domain/validators.py with basic business rule validators
    - _Requirements: 13.1, 13.3, 13.4_
  
  - [x] 2.2 Implement Pix API endpoints and schemas
    - Create api/schemas.py with Pydantic request/response models
    - Create api/endpoints.py with FastAPI router for Pix creation endpoint
    - _Requirements: 13.2_
  
  - [x] 2.3 Add basic test file
    - Create tests/test_pix_creation.py with basic Pix creation test
    - _Requirements: 13.5_

- [x] 3. Implement database layer and data models
  - [x] 3.1 Create SQLAlchemy models and database connection
    - Implement backend/database/models.py with Embedding and AuditLog ORM models
    - Implement backend/database/connection.py with async engine and session factory
    - Add pgvector Vector type support
    - _Requirements: 11.2, 11.3, 12.3, 12.4_
  
  - [x] 3.2 Implement Global State data model
    - Create backend/models/state.py with GlobalState Pydantic model
    - Include all required fields: raw_regulatory_text, change_detected, risk_level, regulatory_model, impacted_files, impact_analysis, technical_spec, kiro_prompt, execution_timestamp, execution_id, error
    - Add JSON serialization configuration
    - _Requirements: 15.1, 15.2, 15.4_
  
  - [x] 3.3 Write property test for Global State serialization
    - **Property 34: Global State Serialization Round-Trip**
    - **Validates: Requirements 15.4**
  
  - [x] 3.4 Create additional data models
    - Implement backend/models/regulatory.py with RegulatoryModel Pydantic model
    - Implement backend/models/impact.py with ImpactedFile and Impact Pydantic models
    - _Requirements: 4.2, 5.3, 6.2_
  
  - [ ]* 3.5 Write property test for Regulatory Model serialization
    - **Property 10: Regulatory Model Round-Trip Serialization**
    - **Validates: Requirements 4.5**

- [x] 4. Implement vector store service
  - [x] 4.1 Create vector store service with search and upsert methods
    - Implement backend/services/vector_store.py with VectorStoreService class
    - Add search_similar method using pgvector cosine similarity
    - Add upsert_embedding method for storing/updating embeddings
    - _Requirements: 11.5, 11.4_
  
  - [x] 4.2 Implement embedding generation service
    - Create backend/services/embeddings.py with EmbeddingService class
    - Use sentence-transformers/all-MiniLM-L6-v2 model
    - Add encode and encode_batch methods
    - _Requirements: 16.4_
  
  - [x] 4.3 Create repository initialization script
    - Implement backend/scripts/init_embeddings.py to generate embeddings for fake Pix repository
    - Iterate through all Python files and store embeddings
    - _Requirements: 11.1, 11.4_
  
  - [ ]* 4.4 Write property test for vector store file coverage
    - **Property 28: Vector Store Contains All Repository Files**
    - **Validates: Requirements 11.1**
  
  - [ ]* 4.5 Write property test for ordered search results
    - **Property 30: Cosine Similarity Search Returns Ordered Results**
    - **Validates: Requirements 11.5**

- [x] 5. Implement LLM integration layer
  - [x] 5.1 Create LLM provider interface and implementations
    - Implement backend/services/llm.py with LLMProvider protocol
    - Implement OllamaLLM class for local Ollama API
    - Implement LocalLLM class as fallback
    - Add get_llm factory function
    - _Requirements: 16.1, 16.2_

- [x] 6. Implement Sentinel Agent
  - [x] 6.1 Create Sentinel Agent with change detection and risk assessment
    - Implement backend/agents/sentinel.py with sentinel_agent function
    - Parse regulatory text using LLM to detect changes
    - Classify risk level as low, medium, or high
    - Update Global State with change_detected and risk_level
    - Add error handling and logging
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 6.2 Write property tests for Sentinel Agent outputs
    - **Property 6: Sentinel Sets Change Detection**
    - **Property 7: Sentinel Sets Valid Risk Level**
    - **Validates: Requirements 3.2, 3.3**

- [x] 7. Implement Translator Agent
  - [x] 7.1 Create Translator Agent with regulatory text structuring
    - Implement backend/agents/translator.py with translator_agent function
    - Extract structured fields using LLM: title, description, requirements, deadlines, affected_systems
    - Create RegulatoryModel object and validate JSON structure
    - Update Global State with regulatory_model
    - Add error handling and logging
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 7.2 Write property tests for Translator Agent outputs
    - **Property 8: Regulatory Model Has Required Fields**
    - **Property 9: Regulatory Model JSON Validity**
    - **Validates: Requirements 4.2, 4.4**

- [x] 8. Implement CodeReader Agent
  - [x] 8.1 Create CodeReader Agent with semantic search
    - Implement backend/agents/code_reader.py with code_reader_agent function
    - Generate search query from regulatory_model
    - Create embedding for query using EmbeddingService
    - Query VectorStoreService for top 10 similar files
    - Update Global State with impacted_files list
    - Handle empty results case
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 8.2 Write property tests for CodeReader Agent outputs
    - **Property 11: CodeReader Returns At Most 10 Files**
    - **Property 12: Impacted Files Have Required Structure**
    - **Validates: Requirements 5.2, 5.3**

- [x] 9. Implement Impact Agent
  - [x] 9.1 Create Impact Agent with technical impact analysis
    - Implement backend/agents/impact.py with impact_agent function
    - For each file in impacted_files, load content and analyze against regulatory_model using LLM
    - Classify impact_type: schema_change, business_logic, validation, api_contract
    - Assess severity: low, medium, high
    - Generate description and suggested_changes
    - Update Global State with impact_analysis list
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 9.2 Write property tests for Impact Agent outputs
    - **Property 13: Impact Analysis Has Required Fields**
    - **Property 14: Impact Type Is Valid**
    - **Property 15: Impact Severity Is Valid**
    - **Validates: Requirements 6.2, 6.3, 6.4**

- [x] 10. Implement SpecGenerator Agent
  - [x] 10.1 Create SpecGenerator Agent with technical specification generation
    - Implement backend/agents/spec_generator.py with spec_generator_agent function
    - Generate Markdown document with sections: overview, affected_components, required_changes, acceptance_criteria, estimated_effort
    - Reference all files from impact_analysis
    - Calculate effort estimate based on severity weights
    - Update Global State with technical_spec
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [ ]* 10.2 Write property tests for SpecGenerator Agent outputs
    - **Property 16: Technical Spec Is Generated**
    - **Property 17: Technical Spec Contains Required Sections**
    - **Property 18: Technical Spec References All Impacted Files**
    - **Property 19: Technical Spec Is Valid Markdown**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4**

- [x] 11. Implement KiroPrompt Agent
  - [x] 11.1 Create KiroPrompt Agent with development prompt generation
    - Implement backend/agents/kiro_prompt.py with kiro_prompt_agent function
    - Generate prompt with sections: CONTEXT, OBJECTIVE, SPECIFIC INSTRUCTIONS, FILE MODIFICATIONS, VALIDATION STEPS, CONSTRAINTS
    - Extract context from regulatory_model
    - Generate step-by-step instructions from impact_analysis
    - List file modifications with specific changes
    - Create validation steps from technical_spec
    - Update Global State with kiro_prompt
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ]* 11.2 Write property tests for KiroPrompt Agent outputs
    - **Property 20: Kiro Prompt Is Generated**
    - **Property 21: Kiro Prompt Contains Required Sections**
    - **Property 22: Kiro Prompt References Source Data**
    - **Validates: Requirements 8.1, 8.2, 8.3**

- [x] 12. Implement LangGraph orchestrator
  - [x] 12.1 Create LangGraph orchestrator with deterministic agent pipeline
    - Implement backend/orchestrator/graph.py with RegulatoryAnalysisGraph class
    - Define StateGraph with GlobalState
    - Add nodes for all six agents: sentinel, translator, code_reader, impact, spec_generator, kiro_prompt
    - Define deterministic edges in sequence: sentinel → translator → code_reader → impact → spec_generator → kiro_prompt → END
    - Implement execute method that compiles and invokes graph
    - Add error handling to halt execution on agent failure
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 12.2 Write property tests for orchestrator behavior
    - **Property 2: Deterministic Agent Execution Sequence**
    - **Property 3: State Propagation Between Agents**
    - **Property 4: State Mutation After Agent Execution**
    - **Property 5: Error Handling Halts Execution**
    - **Validates: Requirements 2.1, 2.2, 2.4, 2.5**

- [x] 13. Implement graph visualization
  - [x] 13.1 Create graph visualizer with Mermaid diagram generation
    - Implement backend/services/graph_visualizer.py with GraphVisualizer class
    - Add generate_mermaid_diagram method that creates Mermaid syntax
    - Include nodes for all six agents with annotations from Global State
    - Add directed edges showing execution sequence
    - Optionally add export_png method if Graphviz available
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 13.2 Write property tests for graph visualization
    - **Property 24: Mermaid Diagram Is Generated**
    - **Property 25: Mermaid Diagram Contains All Agents**
    - **Property 26: Mermaid Diagram Shows Execution Order**
    - **Validates: Requirements 10.1, 10.2, 10.3**

- [x] 14. Implement audit logging service
  - [x] 14.1 Create audit service with save and retrieve methods
    - Implement backend/services/audit.py with AuditService class
    - Add save_execution method to persist Global State to audit_logs table
    - Add retrieve_execution method to load audit log by execution_id
    - Use async SQLAlchemy session
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ]* 14.2 Write property tests for audit logging
    - **Property 31: Audit Log Created Per Execution**
    - **Property 32: Audit Log Contains All Required Fields**
    - **Validates: Requirements 12.1, 12.2**

- [x] 15. Implement FastAPI backend
  - [x] 15.1 Create FastAPI application with main endpoints
    - Implement backend/main.py with FastAPI app
    - Add POST /analyze endpoint that accepts regulatory text, initializes Global State, invokes orchestrator, saves audit log, and returns results
    - Add GET /health endpoint for health checks
    - Add GET /audit/{execution_id} endpoint to retrieve audit logs
    - Add error handling for 400, 500, 503 responses
    - Configure CORS for frontend communication
    - _Requirements: 1.3, 12.1, 14.4_
  
  - [ ]* 15.2 Write unit tests for API endpoints
    - Test /analyze with valid input
    - Test /analyze with empty input (400 error)
    - Test /health endpoint
    - Test /audit/{execution_id} with valid and invalid IDs

- [x] 16. Implement Streamlit frontend
  - [x] 16.1 Create Streamlit app with input section
    - Implement frontend/app.py with Streamlit application
    - Add text area for regulatory text input
    - Add "Analisar Impacto" button
    - Add input validation for empty text
    - Add loading indicator during analysis
    - Implement analyze_text function to call backend POST /analyze endpoint
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 16.2 Create results visualization with 5 tabs
    - Add 5 tabs: "Modelo Regulatório Estruturado", "Impacto no Código", "Especificação Técnica", "Prompt Final para Desenvolvimento", "Fluxo de Execução dos Agentes"
    - Tab 1: Display regulatory_model as formatted JSON
    - Tab 2: Display impact_analysis with expandable sections per file
    - Tab 3: Display technical_spec as rendered Markdown
    - Tab 4: Display kiro_prompt as text
    - Tab 5: Display graph visualization with Mermaid diagram and execution metadata
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 10.4_
  
  - [x] 16.3 Add error handling and user feedback
    - Handle network errors with retry option
    - Handle timeout errors (>2 minutes)
    - Display user-friendly error messages
    - Add success confirmation after analysis completes

- [x] 17. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify Docker Compose startup works correctly
  - Test end-to-end flow with sample regulatory text
  - Ensure all tests pass, ask the user if questions arise

- [x] 18. Create integration tests
  - [x] 18.1 Write end-to-end integration tests
    - Create tests/integration/test_e2e.py
    - Test full pipeline execution with sample regulatory text
    - Verify all agents execute in sequence
    - Verify all outputs are generated
    - Verify audit log is created
    - _Requirements: 2.1, 12.1_
  
  - [ ]* 18.2 Write Docker integration tests
    - Create tests/integration/test_docker.py
    - Test docker-compose startup
    - Test service health checks
    - Test inter-service communication
    - Test database initialization
    - _Requirements: 14.2, 14.3, 14.4, 14.5_
  
  - [ ]* 18.3 Write offline operation test
    - **Property 35: Offline Operation After Setup**
    - **Validates: Requirements 16.5**

- [x] 19. Create test fixtures and sample data
  - [x] 19.1 Create sample regulatory texts
    - Implement tests/fixtures/regulatory_texts.py with various sample texts
    - Include short (100 words), medium (500 words), and long (2000 words) regulations
    - Include texts with explicit deadlines, Pix mentions, and informational content
  
  - [x] 19.2 Create mock responses for testing
    - Implement tests/fixtures/mock_responses.py
    - Add mock LLM responses for each agent
    - Add mock vector search results
    - Add mock database responses

- [x] 20. Add documentation and README files
  - [x] 20.1 Create main README with setup instructions
    - Document prerequisites (Docker, Docker Compose)
    - Document startup command: docker-compose up --build
    - Document access URLs: frontend (8501), backend (8000)
    - Document environment variables and configuration
  
  - [x] 20.2 Create README for fake Pix repository
    - Document repository structure
    - Explain purpose of each module
    - Provide examples of Pix operations
  
  - [x] 20.3 Add inline code documentation
    - Add docstrings to all agents
    - Add docstrings to all services
    - Add docstrings to all API endpoints
    - Add comments for complex logic

- [x] 21. Final checkpoint - Complete system validation
  - Run complete test suite (unit + property + integration)
  - Verify all 35 correctness properties pass
  - Test Docker deployment from scratch
  - Verify offline operation after initial setup
  - Test with multiple sample regulatory texts
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional property-based tests and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties using hypothesis library
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: infrastructure → data → agents → orchestration → frontend
- All code uses Python with FastAPI, Streamlit, LangGraph, and PostgreSQL with pgvector
- The system operates entirely locally without external API dependencies
