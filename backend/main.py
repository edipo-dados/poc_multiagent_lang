"""
FastAPI Backend - Main Application

This module implements the REST API for the regulatory-ai-poc system.
It provides endpoints for regulatory text analysis, health checks, and
audit log retrieval.

Endpoints:
- POST /analyze: Analyze regulatory text and return complete results
- GET /health: Health check for monitoring
- GET /audit/{execution_id}: Retrieve specific audit log

Requirements: 1.3, 12.1, 14.4
"""

import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, UTC
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.models.state import GlobalState
from backend.orchestrator.graph import RegulatoryAnalysisGraph
from backend.services.audit import AuditService
from backend.services.graph_visualizer import GraphVisualizer
from backend.database.connection import AsyncSessionLocal, engine
from backend.database.models import Base


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    
    Startup: Initialize database tables
    Shutdown: Clean up resources
    """
    # Startup
    logger.info("Starting up Regulatory AI POC Backend")
    
    # Create database tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Regulatory AI POC Backend")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Regulatory AI POC Backend",
    description="Multi-agent system for regulatory text analysis and impact assessment",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AnalyzeRequest(BaseModel):
    """Request model for /analyze endpoint."""
    regulatory_text: str = Field(
        description="Regulatory text to analyze",
        min_length=1
    )


class AnalyzeResponse(BaseModel):
    """Response model for /analyze endpoint."""
    execution_id: str = Field(description="Unique execution identifier")
    change_detected: Optional[bool] = Field(description="Whether regulatory changes detected")
    risk_level: Optional[str] = Field(description="Risk level: low, medium, high")
    regulatory_model: Optional[dict] = Field(description="Structured regulatory model")
    impacted_files: list[dict] = Field(description="List of impacted code files")
    impact_analysis: list[dict] = Field(description="Detailed impact analysis")
    technical_spec: Optional[str] = Field(description="Markdown technical specification")
    kiro_prompt: Optional[str] = Field(description="Development prompt")
    graph_visualization: str = Field(description="Mermaid diagram of agent flow")
    timestamp: str = Field(description="Execution timestamp in ISO format")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""
    status: str = Field(description="Overall health status")
    database: str = Field(description="Database connection status")
    vector_store: str = Field(description="Vector store status")
    timestamp: str = Field(description="Health check timestamp")


class AuditResponse(BaseModel):
    """Response model for /audit/{execution_id} endpoint."""
    execution_id: str
    raw_text: str
    change_detected: Optional[bool]
    risk_level: Optional[str]
    structured_model: Optional[dict]
    impacted_files: list[dict]
    impact_analysis: list[dict]
    technical_spec: Optional[str]
    kiro_prompt: Optional[str]
    error: Optional[str]
    timestamp: str


# Request/Response Models
@app.post("/analyze", response_model=AnalyzeResponse, status_code=status.HTTP_200_OK)
async def analyze_regulatory_text(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze regulatory text and return complete results.
    
    This endpoint:
    1. Validates input (non-empty text)
    2. Initializes Global State with execution_id
    3. Invokes LangGraph orchestrator to execute agent pipeline
    4. Generates graph visualization
    5. Saves complete execution to audit log
    6. Returns all results to frontend
    
    Args:
        request: AnalyzeRequest with regulatory_text
        
    Returns:
        AnalyzeResponse with complete analysis results
        
    Raises:
        HTTPException 400: If regulatory text is empty
        HTTPException 500: If agent execution fails
        HTTPException 503: If database is unavailable
        
    Requirements: 1.3, 12.1, 14.4
    """
    logger.info("=== POST /analyze - Starting regulatory text analysis ===")
    
    # Validate input
    if not request.regulatory_text or not request.regulatory_text.strip():
        logger.warning("Empty regulatory text received")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Regulatory text cannot be empty"
        )
    
    logger.info(f"Regulatory text length: {len(request.regulatory_text)} characters")
    
    # Generate unique execution ID
    execution_id = str(uuid.uuid4())
    logger.info(f"Generated execution_id: {execution_id}")
    
    # Initialize Global State
    initial_state = GlobalState(
        raw_regulatory_text=request.regulatory_text,
        execution_id=execution_id,
        execution_timestamp=datetime.now(UTC)
    )
    
    try:
        # Execute agent pipeline
        logger.info("Initializing LangGraph orchestrator")
        orchestrator = RegulatoryAnalysisGraph()
        
        logger.info("Executing agent pipeline")
        final_state = orchestrator.execute(initial_state)
        
        logger.info("Agent pipeline completed successfully")
        
        # Generate graph visualization
        logger.info("Generating graph visualization")
        visualizer = GraphVisualizer()
        graph_viz = visualizer.generate_mermaid_diagram(final_state)
        
        # Save to audit log
        logger.info("Saving execution to audit log")
        async with AsyncSessionLocal() as session:
            audit_service = AuditService(session)
            await audit_service.save_execution(final_state)
        
        logger.info("Audit log saved successfully")
        
        # Build response
        response = AnalyzeResponse(
            execution_id=final_state.execution_id,
            change_detected=final_state.change_detected,
            risk_level=final_state.risk_level,
            regulatory_model=final_state.regulatory_model,
            impacted_files=final_state.impacted_files,
            impact_analysis=final_state.impact_analysis,
            technical_spec=final_state.technical_spec,
            kiro_prompt=final_state.kiro_prompt,
            graph_visualization=graph_viz,
            timestamp=final_state.execution_timestamp.isoformat(),
            error=final_state.error
        )
        
        logger.info("=== POST /analyze - Analysis completed successfully ===")
        return response
        
    except RuntimeError as e:
        # Agent execution failure
        logger.error(f"Agent execution failed: {str(e)}", exc_info=True)
        
        # Try to save partial state to audit log
        try:
            async with AsyncSessionLocal() as session:
                audit_service = AuditService(session)
                await audit_service.save_execution(initial_state)
            logger.info("Partial state saved to audit log")
        except Exception as audit_error:
            logger.error(f"Failed to save partial state: {str(audit_error)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )
        
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error during analysis: {str(e)}", exc_info=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for monitoring.
    
    Checks:
    - Overall service status
    - Database connection
    - Vector store availability
    
    Returns:
        HealthResponse with status of all components
        
    Requirements: 14.4
    """
    logger.debug("GET /health - Health check requested")
    
    # Check database connection
    db_status = "connected"
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            await session.execute("SELECT 1")
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "disconnected"
    
    # Check vector store (same as database for now)
    vector_store_status = "ready" if db_status == "connected" else "unavailable"
    
    # Overall status
    overall_status = "healthy" if db_status == "connected" else "degraded"
    
    response = HealthResponse(
        status=overall_status,
        database=db_status,
        vector_store=vector_store_status,
        timestamp=datetime.now(UTC).isoformat()
    )
    
    logger.debug(f"Health check result: {overall_status}")
    return response


@app.get("/audit/{execution_id}", response_model=AuditResponse, status_code=status.HTTP_200_OK)
async def get_audit_log(execution_id: str) -> AuditResponse:
    """
    Retrieve specific audit log entry by execution_id.
    
    Args:
        execution_id: Unique identifier of the execution
        
    Returns:
        AuditResponse with complete audit log data
        
    Raises:
        HTTPException 404: If execution_id not found
        HTTPException 503: If database is unavailable
        
    Requirements: 12.1
    """
    logger.info(f"GET /audit/{execution_id} - Retrieving audit log")
    
    try:
        # Retrieve from database
        async with AsyncSessionLocal() as session:
            audit_service = AuditService(session)
            state = await audit_service.retrieve_execution(execution_id)
        
        if state is None:
            logger.warning(f"Audit log not found for execution_id: {execution_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution not found: {execution_id}"
            )
        
        # Build response
        response = AuditResponse(
            execution_id=state.execution_id,
            raw_text=state.raw_regulatory_text,
            change_detected=state.change_detected,
            risk_level=state.risk_level,
            structured_model=state.regulatory_model,
            impacted_files=state.impacted_files,
            impact_analysis=state.impact_analysis,
            technical_spec=state.technical_spec,
            kiro_prompt=state.kiro_prompt,
            error=state.error,
            timestamp=state.execution_timestamp.isoformat()
        )
        
        logger.info(f"Audit log retrieved successfully for execution_id: {execution_id}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Database or other error
        logger.error(f"Failed to retrieve audit log: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable"
        )
