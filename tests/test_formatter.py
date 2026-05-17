"""Tests for the Rich renderer.

We don't snapshot the exact box-drawing characters — those change with Rich
versions. We assert the meaningful pieces appear in the rendered output.
"""

from __future__ import annotations

import io
import json

import pytest
from rich.console import Console

from cli import formatter
from cli.client import AnalysisResponse
from cli.errors import AuthError


def _render(callable_, *args, **kwargs) -> str:
    """Swap the formatter's console for a recording one and capture output."""
    buffer = io.StringIO()
    recorded = Console(file=buffer, width=120, force_terminal=False, color_system=None)
    original = formatter.console
    formatter.console = recorded
    try:
        callable_(*args, **kwargs)
    finally:
        formatter.console = original
    return buffer.getvalue()


def _render_error(err) -> str:
    buffer = io.StringIO()
    recorded = Console(file=buffer, width=120, force_terminal=False, color_system=None)
    original = formatter.error_console
    formatter.error_console = recorded
    try:
        formatter.render_error(err)
    finally:
        formatter.error_console = original
    return buffer.getvalue()


# --------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------- #
@pytest.mark.parametrize("label", ["LOW", "MEDIUM", "HIGH"])
def test_render_summary_includes_risk_label(label):
    response = AnalysisResponse(
        report_id="abc",
        dashboard_url="http://x/report/abc",
        risk_score={"LOW": 20, "MEDIUM": 55, "HIGH": 82}[label],
        risk_label=label,
        impacted_node_count=14,
        status="COMPLETE",
    )
    output = _render(formatter.render_summary, response)
    assert label in output
    assert "PRISM" in output
    assert "Risk Score" in output
    assert "http://x/report/abc" in output
    assert "14 impacted nodes" in output


def test_render_summary_warns_on_partial_status():
    response = AnalysisResponse(
        report_id="abc",
        dashboard_url="http://x/report/abc",
        risk_score=55,
        risk_label="MEDIUM",
        impacted_node_count=8,
        status="PARTIAL",
    )
    output = _render(formatter.render_summary, response)
    assert "AI service unavailable" in output


def test_render_summary_singular_impacted_node():
    response = AnalysisResponse(
        report_id="abc",
        dashboard_url="http://x/report/abc",
        risk_score=10,
        risk_label="LOW",
        impacted_node_count=1,
        status="COMPLETE",
    )
    output = _render(formatter.render_summary, response)
    assert "1 impacted node identified" in output


# --------------------------------------------------------------------- #
# Error
# --------------------------------------------------------------------- #
def test_render_error_includes_message_and_hint():
    err = AuthError("Bad credentials")
    output = _render_error(err)
    assert "Bad credentials" in output
    assert "Hint" in output


# --------------------------------------------------------------------- #
# JSON
# --------------------------------------------------------------------- #
def test_render_json_emits_valid_json(capsys):
    response = AnalysisResponse(
        report_id="abc",
        dashboard_url="http://x/report/abc",
        risk_score=82,
        risk_label="HIGH",
        impacted_node_count=14,
        status="COMPLETE",
    )
    formatter.render_json(response)
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed["report_id"] == "abc"
    assert parsed["risk_label"] == "HIGH"
    assert parsed["risk_score"] == 82


def test_render_error_json_writes_to_stderr(capsys):
    err = AuthError("nope")
    formatter.render_error_json(err)
    captured = capsys.readouterr()
    parsed = json.loads(captured.err)
    assert parsed["error"] == "nope"
    assert "hint" in parsed
