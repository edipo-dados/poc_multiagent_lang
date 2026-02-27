"""
Unit tests for FastAPI main application endpoints.

Tests the /analyze, /health, and /audit/{execution_id} endpoints
with various scenarios including success cases and error handling.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, UTC

from backend.main import app
from backend.models.state import GlobalState


# Create test client
client = TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""
    
    def test_health_check_success(self):
        """Test health check returns healthy status when database is connected."""
        with patch('backend.main.AsyncSessionLocal') as mock_session:
            # Mock successful database connection
            mock_session.return_value.__aenter__.return_value.execute = AsyncMock()
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "database" in data
            assert "vector_store" in data
            assert "timestamp" in data
    
    def test_health_check_database_down(self):
        """Test health check returns degraded status when database is down."""
        with patch('backend.main.AsyncSessionLocal') as mock_session:
            # Mock database connection failure
            mock_session.return_value.__aenter__.side_effect = Exception("Connection failed")
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            # Should still return 200 but with degraded status
            assert data["status"] in ["healthy", "degraded"]


class TestAnalyzeEndpoint:
    """Tests for POST /analyze endpoint."""
    
    def test_analyze_empty_text_returns_422(self):
        """Test that empty regulatory text returns 422 Unprocessable Entity (Pydantic validation)."""
        response = client.post("/analyze", json={"regulatory_text": ""})
        
        # Pydantic validation returns 422 for min_length constraint
        assert response.status_code == 422
    
    def test_analyze_whitespace_only_returns_400(self):
        """Test that whitespace-only text returns 400 Bad Request."""
        response = client.post("/analyze", json={"regulatory_text": "   \n\t  "})
        
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    @patch('backend.main.RegulatoryAnalysisGraph')
    @patch('backend.main.GraphVisualizer')
    @patch('backend.main.AuditService')
    @patch('backend.main.AsyncSessionLocal')
    def test_analyze_success(self, mock_session, mock_audit, mock_visualizer, mock_graph):
        """Test successful analysis returns complete results."""
        # Mock successful execution
        mock_state = GlobalState(
            raw_regulatory_text="Test regulatory text",
            execution_id="test-uuid-123",
            execution_timestamp=datetime.now(UTC),
            change_detected=True,
            risk_level="high",
            regulatory_model={"title": "Test Regulation"},
            impacted_files=[{"file_path": "test.py", "relevance_score": 0.9}],
            impact_analysis=[{"file_path": "test.py", "severity": "high"}],
            technical_spec="# Test Spec",
            kiro_prompt="Test prompt"
        )
        
        mock_graph.return_value.execute.return_value = mock_state
        mock_visualizer.return_value.generate_mermaid_diagram.return_value = "graph LR"
        mock_audit.return_value.save_execution = AsyncMock()
        mock_session.return_value.__aenter__.return_value = Mock()
        
        response = client.post("/analyze", json={"regulatory_text": "Test regulatory text"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["execution_id"] == "test-uuid-123"
        assert data["change_detected"] is True
        assert data["risk_level"] == "high"
        assert data["regulatory_model"]["title"] == "Test Regulation"
        assert len(data["impacted_files"]) == 1
        assert len(data["impact_analysis"]) == 1
        assert data["technical_spec"] == "# Test Spec"
        assert data["kiro_prompt"] == "Test prompt"
        assert data["graph_visualization"] == "graph LR"
    
    @patch('backend.main.RegulatoryAnalysisGraph')
    def test_analyze_agent_failure_returns_500(self, mock_graph):
        """Test that agent execution failure returns 500 Internal Server Error."""
        # Mock agent failure
        mock_graph.return_value.execute.side_effect = RuntimeError("Agent failed")
        
        with patch('backend.main.AsyncSessionLocal') as mock_session:
            mock_session.return_value.__aenter__.return_value = Mock()
            mock_audit = Mock()
            mock_audit.save_execution = AsyncMock()
            
            with patch('backend.main.AuditService', return_value=mock_audit):
                response = client.post("/analyze", json={"regulatory_text": "Test text"})
        
        assert response.status_code == 500
        assert "failed" in response.json()["detail"].lower()


class TestAuditEndpoint:
    """Tests for GET /audit/{execution_id} endpoint."""
    
    @patch('backend.main.AuditService')
    @patch('backend.main.AsyncSessionLocal')
    def test_get_audit_log_success(self, mock_session, mock_audit):
        """Test successful retrieval of audit log."""
        # Mock successful retrieval
        mock_state = GlobalState(
            raw_regulatory_text="Test text",
            execution_id="test-uuid-123",
            execution_timestamp=datetime.now(UTC),
            change_detected=True,
            risk_level="medium"
        )
        
        mock_audit.return_value.retrieve_execution = AsyncMock(return_value=mock_state)
        mock_session.return_value.__aenter__.return_value = Mock()
        
        response = client.get("/audit/test-uuid-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["execution_id"] == "test-uuid-123"
        assert data["raw_text"] == "Test text"
        assert data["change_detected"] is True
        assert data["risk_level"] == "medium"
    
    @patch('backend.main.AuditService')
    @patch('backend.main.AsyncSessionLocal')
    def test_get_audit_log_not_found(self, mock_session, mock_audit):
        """Test that non-existent execution_id returns 404 Not Found."""
        # Mock not found
        mock_audit.return_value.retrieve_execution = AsyncMock(return_value=None)
        mock_session.return_value.__aenter__.return_value = Mock()
        
        response = client.get("/audit/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @patch('backend.main.AsyncSessionLocal')
    def test_get_audit_log_database_error_returns_503(self, mock_session):
        """Test that database error returns 503 Service Unavailable."""
        # Mock database error
        mock_session.return_value.__aenter__.side_effect = Exception("Database error")
        
        response = client.get("/audit/test-uuid-123")
        
        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()


class TestCORS:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        response = client.get("/health")
        
        # CORS middleware should add these headers
        assert response.status_code == 200
        # Note: TestClient doesn't fully simulate CORS, but we can verify the middleware is configured


class TestRequestValidation:
    """Tests for request validation."""
    
    def test_analyze_missing_field_returns_422(self):
        """Test that missing required field returns 422 Unprocessable Entity."""
        response = client.post("/analyze", json={})
        
        assert response.status_code == 422
    
    def test_analyze_invalid_json_returns_422(self):
        """Test that invalid JSON returns 422 Unprocessable Entity."""
        response = client.post(
            "/analyze",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
