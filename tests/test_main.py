"""Tests for the Typer commands.

We patch ``AnalysisClient`` so the CLI exercises its real flow but doesn't
hit the network.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from cli import __version__
from cli.client import AnalysisResponse
from cli.errors import AuthError, BackendUnreachable
from cli.main import app

runner = CliRunner()


class _FakeClient:
    """Stand-in for ``AnalysisClient`` used by the main-flow tests."""

    last_request: dict[str, object] = {}

    def __init__(
        self,
        *,
        health: bool = True,
        response: AnalysisResponse | None = None,
        raise_on_run: Exception | None = None,
    ) -> None:
        self._health = health
        self._response = response or AnalysisResponse(
            report_id="abc",
            dashboard_url="http://x/report/abc",
            risk_score=82,
            risk_label="HIGH",
            impacted_node_count=14,
            status="COMPLETE",
        )
        self._raise = raise_on_run

    def check_health(self) -> bool:
        return self._health

    def run(self, pr_identifier, repository_url, github_token=None):
        type(self).last_request = {
            "pr_identifier": pr_identifier,
            "repository_url": repository_url,
            "github_token": github_token,
        }
        if self._raise is not None:
            raise self._raise
        return self._response

    def close(self) -> None:
        pass


def _patch_client(monkeypatch, **kwargs) -> type[_FakeClient]:
    """Replace ``AnalysisClient`` in main with a fake factory."""

    def factory(*_args, **_kwargs):
        return _FakeClient(**kwargs)

    monkeypatch.setattr("cli.main.AnalysisClient", factory)
    return _FakeClient


def _disable_browser(monkeypatch) -> None:
    monkeypatch.setattr("cli.main.webbrowser.open", lambda *_a, **_k: None)


# --------------------------------------------------------------------- #
# Top-level surface
# --------------------------------------------------------------------- #
def test_help_lists_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "analyze" in result.stdout
    assert "demo" in result.stdout
    assert "version" in result.stdout


def test_version_prints_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_json_flag_is_hidden_from_help():
    result = runner.invoke(app, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "--json" not in result.stdout


# --------------------------------------------------------------------- #
# analyze
# --------------------------------------------------------------------- #
def test_analyze_requires_repo(monkeypatch):
    # Make sure no .env leaks in via PRISM_REPO_URL.
    monkeypatch.delenv("PRISM_REPO_URL", raising=False)
    _patch_client(monkeypatch)
    result = runner.invoke(app, ["analyze", "pr-1"], env={"PRISM_REPO_URL": ""})
    assert result.exit_code == 1


def test_analyze_happy_path(monkeypatch):
    fake = _patch_client(monkeypatch)
    _disable_browser(monkeypatch)

    result = runner.invoke(
        app,
        [
            "analyze",
            "pr-142",
            "--repo",
            "https://github.com/owner/repo",
            "--token",
            "ghp_x",
            "--backend",
            "http://localhost:8000",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert fake.last_request["pr_identifier"] == "pr-142"
    assert fake.last_request["repository_url"] == "https://github.com/owner/repo"
    assert fake.last_request["github_token"] == "ghp_x"


def test_analyze_json_output(monkeypatch):
    _patch_client(monkeypatch)
    result = runner.invoke(
        app,
        [
            "analyze",
            "pr-142",
            "--repo",
            "https://github.com/owner/repo",
            "--json",
        ],
    )
    assert result.exit_code == 0
    import json

    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["risk_label"] == "HIGH"
    assert payload["report_id"] == "abc"


def test_analyze_fails_fast_when_backend_down(monkeypatch):
    _patch_client(monkeypatch, health=False)
    result = runner.invoke(
        app,
        ["analyze", "pr-142", "--repo", "https://github.com/owner/repo"],
    )
    assert result.exit_code == 1


def test_analyze_surfaces_auth_error(monkeypatch):
    _patch_client(monkeypatch, raise_on_run=AuthError("Bad credentials"))
    result = runner.invoke(
        app,
        ["analyze", "pr-142", "--repo", "https://github.com/owner/repo"],
    )
    assert result.exit_code == 1


def test_analyze_json_error_emits_json(monkeypatch):
    _patch_client(monkeypatch, raise_on_run=BackendUnreachable("nope"))
    result = runner.invoke(
        app,
        [
            "analyze",
            "pr-142",
            "--repo",
            "https://github.com/owner/repo",
            "--json",
        ],
    )
    assert result.exit_code == 1
    # The JSON error is printed to stderr; CliRunner merges by default.
    import json

    # Look for a JSON-shaped line in mixed output.
    for line in (result.stdout + "\n" + (result.stderr or "")).splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            payload = json.loads(line)
            assert "error" in payload
            return
    pytest.fail("no JSON error line found")


# --------------------------------------------------------------------- #
# demo
# --------------------------------------------------------------------- #
def test_demo_uses_fixture(monkeypatch):
    fake = _patch_client(monkeypatch)
    _disable_browser(monkeypatch)

    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 0
    assert fake.last_request["pr_identifier"] == "pr-142"
    assert "prism-demo/payment-service" in fake.last_request["repository_url"]


# --------------------------------------------------------------------- #
# git-remote auto-detection
# --------------------------------------------------------------------- #
def test_analyze_uses_detected_remote(monkeypatch):
    """When --repo is omitted, the CLI must pick up `git remote get-url origin`."""
    monkeypatch.delenv("PRISM_REPO_URL", raising=False)
    fake = _patch_client(monkeypatch)
    _disable_browser(monkeypatch)
    monkeypatch.setattr(
        "cli.main.detect_git_remote",
        lambda *_a, **_k: "https://github.com/auto/detected",
    )

    result = runner.invoke(app, ["analyze", "pr-1"], env={"PRISM_REPO_URL": ""})

    assert result.exit_code == 0, result.stdout
    assert fake.last_request["repository_url"] == "https://github.com/auto/detected"
    assert "Detected repo:" in result.stdout


def test_analyze_fails_when_no_remote(monkeypatch):
    """No --repo, no env var, no git origin → ConfigError with the new hint."""
    monkeypatch.delenv("PRISM_REPO_URL", raising=False)
    _patch_client(monkeypatch)
    monkeypatch.setattr("cli.main.detect_git_remote", lambda *_a, **_k: None)

    result = runner.invoke(app, ["analyze", "pr-1"], env={"PRISM_REPO_URL": ""})

    assert result.exit_code == 1
    combined = result.stdout + (result.stderr or "")
    assert "origin" in combined.lower() or "repo" in combined.lower()


def test_analyze_json_suppresses_detected_line(monkeypatch):
    """`--json` consumers must not see the `Detected repo:` chatter."""
    monkeypatch.delenv("PRISM_REPO_URL", raising=False)
    _patch_client(monkeypatch)
    _disable_browser(monkeypatch)
    monkeypatch.setattr(
        "cli.main.detect_git_remote",
        lambda *_a, **_k: "https://github.com/auto/detected",
    )

    result = runner.invoke(app, ["analyze", "pr-1", "--json"], env={"PRISM_REPO_URL": ""})

    assert result.exit_code == 0
    assert "Detected repo:" not in result.stdout


# --------------------------------------------------------------------- #
# backend sub-app
# --------------------------------------------------------------------- #
def test_backend_serve_help():
    """Sub-app is wired in and its help renders without launching uvicorn."""
    result = runner.invoke(app, ["backend", "--help"])
    assert result.exit_code == 0
    assert "serve" in result.stdout


def test_backend_serve_command_help():
    result = runner.invoke(app, ["backend", "serve", "--help"])
    assert result.exit_code == 0
    assert "--host" in result.stdout
    assert "--port" in result.stdout


def test_backend_serve_reports_missing_extra(monkeypatch):
    """If FastAPI/uvicorn aren't importable, the command fails with a clear hint."""
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "uvicorn" or name.startswith("backend.app"):
            raise ImportError(f"No module named {name!r}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    result = runner.invoke(app, ["backend", "serve"])
    assert result.exit_code == 1
    combined = result.stdout + (result.stderr or "")
    assert "[backend]" in combined or "backend" in combined.lower()
