"""
Pytest Configuration and Fixtures

Shared fixtures for all CLI tests.
"""

import pytest
from unittest.mock import Mock
import httpx

from cli.client import AnalysisResponse


@pytest.fixture
def mock_analysis_response():
    """Create a mock successful analysis response."""
    return AnalysisResponse(
        report_id="test-report-123",
        dashboard_url="http://localhost:3000/report/test-report-123",
        risk_score=75,
        risk_label="HIGH",
        impacted_node_count=12,
        status="COMPLETE"
    )


@pytest.fixture
def mock_partial_response():
    """Create a mock partial analysis response (IBM Bob unavailable)."""
    return AnalysisResponse(
        report_id="test-report-456",
        dashboard_url="http://localhost:3000/report/test-report-456",
        risk_score=45,
        risk_label="MEDIUM",
        impacted_node_count=6,
        status="PARTIAL"
    )


@pytest.fixture
def mock_low_risk_response():
    """Create a mock low risk analysis response."""
    return AnalysisResponse(
        report_id="test-report-789",
        dashboard_url="http://localhost:3000/report/test-report-789",
        risk_score=25,
        risk_label="LOW",
        impacted_node_count=3,
        status="COMPLETE"
    )


@pytest.fixture
def mock_httpx_client_success(mock_analysis_response):
    """Create a mock httpx client that returns successful responses."""
    def create_response(request):
        # Health check
        if request.url.path == "/healthz":
            return httpx.Response(200, json={"ok": True})
        
        # Analysis endpoint
        if request.url.path == "/api/analysis/run":
            return httpx.Response(200, json=mock_analysis_response.model_dump())
        
        return httpx.Response(404)
    
    return httpx.MockTransport(create_response)


@pytest.fixture
def mock_httpx_client_backend_down():
    """Create a mock httpx client that simulates backend being down."""
    def create_response(request):
        raise httpx.ConnectError("Connection refused")
    
    return httpx.MockTransport(create_response)


@pytest.fixture
def mock_httpx_client_timeout():
    """Create a mock httpx client that simulates timeout."""
    def create_response(request):
        raise httpx.TimeoutException("Request timed out")
    
    return httpx.MockTransport(create_response)


@pytest.fixture
def mock_httpx_client_auth_error():
    """Create a mock httpx client that returns 401 Unauthorized."""
    def create_response(request):
        if request.url.path == "/healthz":
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(401, json={"detail": "Invalid GitHub token"})
    
    return httpx.MockTransport(create_response)


@pytest.fixture
def mock_httpx_client_not_found():
    """Create a mock httpx client that returns 404 Not Found."""
    def create_response(request):
        if request.url.path == "/healthz":
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(404, json={"detail": "PR not found"})
    
    return httpx.MockTransport(create_response)


@pytest.fixture
def mock_httpx_client_server_error():
    """Create a mock httpx client that returns 500 Server Error."""
    def create_response(request):
        if request.url.path == "/healthz":
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(500, json={"detail": "Internal server error"})
    
    return httpx.MockTransport(create_response)

# Made with Bob
