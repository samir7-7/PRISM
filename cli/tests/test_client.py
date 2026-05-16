"""
Tests for cli/client.py

Tests the HTTP client, response parsing, and error handling.
"""

import pytest
import httpx

from cli.client import AnalysisClient, AnalysisResponse
from cli.errors import (
    BackendUnreachable,
    BackendTimeout,
    BackendBadRequest,
    AuthError,
    NotFoundError,
    BackendServerError,
    ValidationError,
)


def test_analysis_response_model():
    """Test AnalysisResponse model validation."""
    response = AnalysisResponse(
        report_id="test-123",
        dashboard_url="http://localhost:3000/report/test-123",
        risk_score=50,
        risk_label="MEDIUM",
        impacted_node_count=5,
        status="COMPLETE"
    )
    
    assert response.report_id == "test-123"
    assert response.risk_score == 50
    assert response.risk_label == "MEDIUM"
    assert response.status == "COMPLETE"


def test_analysis_response_validation_risk_score():
    """Test that risk_score must be between 0 and 100."""
    with pytest.raises(Exception):  # Pydantic validation error
        AnalysisResponse(
            report_id="test",
            dashboard_url="http://test",
            risk_score=150,  # Invalid: > 100
            risk_label="HIGH",
            impacted_node_count=5,
            status="COMPLETE"
        )


def test_health_check_success(mock_httpx_client_success):
    """Test successful health check."""
    client = AnalysisClient("http://localhost:8000", timeout=60)
    client._client = httpx.Client(transport=mock_httpx_client_success)
    
    assert client.check_health() is True
    
    client.close()


def test_health_check_failure(mock_httpx_client_backend_down):
    """Test health check when backend is down."""
    client = AnalysisClient("http://localhost:8000", timeout=60)
    client._client = httpx.Client(transport=mock_httpx_client_backend_down)
    
    assert client.check_health() is False
    
    client.close()


def test_run_analysis_success(mock_httpx_client_success, mock_analysis_response):
    """Test successful analysis request."""
    client = AnalysisClient("http://localhost:8000", timeout=60)
    client._client = httpx.Client(transport=mock_httpx_client_success)
    
    response = client.run(
        pr_identifier="pr-142",
        repository_url="https://github.com/owner/repo",
        github_token="ghp_test_token"
    )
    
    assert isinstance(response, AnalysisResponse)
    assert response.report_id == mock_analysis_response.report_id
    assert response.risk_score == mock_analysis_response.risk_score
    assert response.risk_label == mock_analysis_response.risk_label
    
    client.close()


def test_run_analysis_without_token(mock_httpx_client_success):
    """Test analysis request without GitHub token."""
    client = AnalysisClient("http://localhost:8000", timeout=60)
    client._client = httpx.Client(transport=mock_httpx_client_success)
    
    response = client.run(
        pr_identifier="pr-142",
        repository_url="https://github.com/owner/repo",
        github_token=None
    )
    
    assert isinstance(response, AnalysisResponse)
    
    client.close()


def test_run_analysis_backend_unreachable(mock_httpx_client_backend_down):
    """Test analysis when backend is unreachable."""
    client = AnalysisClient("http://localhost:8000", timeout=60)
    client._client = httpx.Client(transport=mock_httpx_client_backend_down)
    
    with pytest.raises(BackendUnreachable) as exc_info:
        client.run(
            pr_identifier="pr-142",
            repository_url="https://github.com/owner/repo"
        )
    
    assert "Cannot reach PRISM backend" in str(exc_info.value)
    
    client.close()


def test_run_analysis_timeout(mock_httpx_client_timeout):
    """Test analysis when request times out."""
    client = AnalysisClient("http://localhost:8000", timeout=60)
    client._client = httpx.Client(transport=mock_httpx_client_timeout)
    
    with pytest.raises(BackendTimeout) as exc_info:
        client.run(
            pr_identifier="pr-142",
            repository_url="https://github.com/owner/repo"
        )
    
    assert "timed out after 60 seconds" in str(exc_info.value)
    
    client.close()


def test_run_analysis_auth_error(mock_httpx_client_auth_error):
    """Test analysis with authentication error."""
    client = AnalysisClient("http://localhost:8000", timeout=60)
    client._client = httpx.Client(transport=mock_httpx_client_auth_error)
    
    with pytest.raises(AuthError) as exc_info:
        client.run(
            pr_identifier="pr-142",
            repository_url="https://github.com/owner/repo",
            github_token="invalid_token"
        )
    
    assert "authentication failed" in str(exc_info.value).lower()
    
    client.close()


def test_run_analysis_not_found(mock_httpx_client_not_found):
    """Test analysis when PR is not found."""
    client = AnalysisClient("http://localhost:8000", timeout=60)
    client._client = httpx.Client(transport=mock_httpx_client_not_found)
    
    with pytest.raises(NotFoundError) as exc_info:
        client.run(
            pr_identifier="pr-999",
            repository_url="https://github.com/owner/repo"
        )
    
    assert "not found" in str(exc_info.value).lower()
    
    client.close()


def test_run_analysis_server_error(mock_httpx_client_server_error):
    """Test analysis when backend returns server error."""
    client = AnalysisClient("http://localhost:8000", timeout=60)
    client._client = httpx.Client(transport=mock_httpx_client_server_error)
    
    with pytest.raises(BackendServerError) as exc_info:
        client.run(
            pr_identifier="pr-142",
            repository_url="https://github.com/owner/repo"
        )
    
    assert "server error" in str(exc_info.value).lower()
    
    client.close()


def test_client_context_manager(mock_httpx_client_success):
    """Test AnalysisClient as context manager."""
    with AnalysisClient("http://localhost:8000", timeout=60) as client:
        client._client = httpx.Client(transport=mock_httpx_client_success)
        assert client.check_health() is True
    
    # Client should be closed after context


def test_client_initialization():
    """Test client initialization with different parameters."""
    client = AnalysisClient("http://localhost:8000", timeout=30)
    assert client.backend_url == "http://localhost:8000"
    assert client.timeout == 30
    client.close()
    
    # Test URL normalization (trailing slash removal)
    client = AnalysisClient("http://localhost:8000/", timeout=60)
    assert client.backend_url == "http://localhost:8000"
    client.close()

# Made with Bob
