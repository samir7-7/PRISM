"""Shared pytest fixtures."""

from __future__ import annotations

import httpx
import pytest

from cli.client import AnalysisClient

# Canonical successful response — used by multiple test files.
SUCCESS_BODY = {
    "report_id": "test123",
    "dashboard_url": "http://localhost:3000/report/test123",
    "risk_score": 50,
    "risk_label": "MEDIUM",
    "impacted_node_count": 5,
    "status": "COMPLETE",
}


def make_client(handler) -> AnalysisClient:
    """Build an ``AnalysisClient`` whose transport calls ``handler(request)``."""
    transport = httpx.MockTransport(handler)
    return AnalysisClient(backend_url="http://test", timeout=5.0, transport=transport)


@pytest.fixture
def success_handler():
    """Default handler that returns ``SUCCESS_BODY`` for any request."""

    def _handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/healthz":
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(200, json=SUCCESS_BODY)

    return _handler
