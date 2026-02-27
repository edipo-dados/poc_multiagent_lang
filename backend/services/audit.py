"""
Audit Service for persisting and retrieving execution logs.

Provides methods for saving complete analysis executions to the audit_logs
table and retrieving them by execution_id for compliance tracking.

Requirements: 12.1, 12.2, 12.3, 12.4, 12.5
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database.models import AuditLog
from backend.models.state import GlobalState


class AuditService:
    """
    Service for managing audit logs of analysis executions.
    
    Persists complete Global State to PostgreSQL for compliance tracking
    and debugging. Each execution creates one audit log entry.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize audit service with database session.
        
        Args:
            session: Async SQLAlchemy session for database operations
        """
        self.session = session
    
    async def save_execution(self, state: GlobalState) -> str:
        """
        Persist Global State to audit_logs table.
        
        Creates a new audit log entry with all inputs, intermediate results,
        and final outputs from the analysis execution. Stores JSON fields
        as JSONB in PostgreSQL for efficient querying.
        
        Args:
            state: GlobalState object containing complete execution data
            
        Returns:
            execution_id: Unique identifier for the saved audit log
            
        Requirements: 12.1, 12.2, 12.3, 12.4
        """
        # Create audit log entry from Global State
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
            error=state.error,
            timestamp=state.execution_timestamp
        )
        
        # Add to session and commit
        self.session.add(audit_entry)
        await self.session.commit()
        
        return state.execution_id
    
    async def retrieve_execution(self, execution_id: str) -> Optional[GlobalState]:
        """
        Load audit log by execution_id and reconstruct Global State.
        
        Retrieves a specific audit log entry from the database and
        reconstructs the GlobalState object with all fields populated.
        
        Args:
            execution_id: Unique identifier of the execution to retrieve
            
        Returns:
            GlobalState object if found, None otherwise
            
        Requirements: 12.3, 12.4
        """
        # Query audit log by execution_id
        stmt = select(AuditLog).where(AuditLog.execution_id == execution_id)
        result = await self.session.execute(stmt)
        audit_entry = result.scalar_one_or_none()
        
        if audit_entry is None:
            return None
        
        # Reconstruct Global State from audit log
        state = GlobalState(
            raw_regulatory_text=audit_entry.raw_text,
            change_detected=audit_entry.change_detected,
            risk_level=audit_entry.risk_level,
            regulatory_model=audit_entry.structured_model,
            impacted_files=audit_entry.impacted_files or [],
            impact_analysis=audit_entry.impact_analysis or [],
            technical_spec=audit_entry.technical_spec,
            kiro_prompt=audit_entry.kiro_prompt,
            execution_timestamp=audit_entry.timestamp,
            execution_id=audit_entry.execution_id,
            error=audit_entry.error
        )
        
        return state
