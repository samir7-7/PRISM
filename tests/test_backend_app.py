"""Integration tests for the bundled FastAPI backend.

Guarded by ``pytest.importorskip("fastapi")`` so the lean install path that
omits the ``[backend]`` extras keeps green. The TestClient exercises the
real ASGI surface — same code path uvicorn would serve in production.
"""

from __future__ import annotations

import httpx
import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from backend.app import app  # noqa: E402
from cli.demo_fixture import DEMO_PR_ID, DEMO_REPO_URL  # noqa: E402

client = TestClient(app)


# --------------------------------------------------------------------- #
# /healthz
# --------------------------------------------------------------------- #
def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


# --------------------------------------------------------------------- #
# /api/analysis/run — demo passthrough
# --------------------------------------------------------------------- #
def test_run_demo_returns_canned_response():
    resp = client.post(
        "/api/analysis/run",
        json={"pr_identifier": DEMO_PR_ID, "repository_url": DEMO_REPO_URL},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_score"] == 82
    assert body["risk_label"] == "HIGH"
    assert body["impacted_node_count"] == 14
    assert body["status"] == "COMPLETE"


# --------------------------------------------------------------------- #
# /api/analysis/run — real path (GitHub fetch mocked)
# --------------------------------------------------------------------- #
def test_run_complete_path(monkeypatch):
    fake_files = [
        {"additions": 100, "deletions": 50},
        {"additions": 10, "deletions": 0},
    ]
    monkeypatch.setattr(
        "backend.analysis.fetch_pr_files",
        lambda *a, **k: fake_files,
    )
    resp = client.post(
        "/api/analysis/run",
        json={"pr_identifier": "pr-9", "repository_url": "https://github.com/owner/repo"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "COMPLETE"
    assert body["impacted_node_count"] == 2


def test_run_partial_when_github_raises(monkeypatch):
    def _boom(*_a, **_k):
        raise httpx.HTTPError("rate limited")

    monkeypatch.setattr("backend.analysis.fetch_pr_files", _boom)
    resp = client.post(
        "/api/analysis/run",
        json={"pr_identifier": "pr-9", "repository_url": "https://github.com/owner/repo"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "PARTIAL"


# --------------------------------------------------------------------- #
# /api/analysis/run — bad input
# --------------------------------------------------------------------- #
def test_run_missing_pr_identifier_is_422():
    resp = client.post(
        "/api/analysis/run",
        json={"repository_url": "https://github.com/owner/repo"},
    )
    assert resp.status_code == 422


def test_run_bad_repo_url_is_422():
    resp = client.post(
        "/api/analysis/run",
        json={"pr_identifier": "pr-1", "repository_url": "not a url"},
    )
    assert resp.status_code == 422
