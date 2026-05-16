"""Cover the interactive spinner branch of ``with_progress``.

By default ``sys.stdout.isatty()`` is False under pytest, so the spinner
short-circuits. We force it into the interactive branch with monkeypatch and
swap in a recording console.
"""

from __future__ import annotations

import io

from rich.console import Console

from cli import formatter


def test_with_progress_no_tty_is_noop(monkeypatch):
    """Non-interactive callers must not see spinner output."""
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)

    buffer = io.StringIO()
    recorded = Console(file=buffer, width=80, force_terminal=False, color_system=None)
    monkeypatch.setattr(formatter, "console", recorded)

    with formatter.with_progress(stages=["Step one", "Step two"]):
        pass

    assert buffer.getvalue() == ""


def test_with_progress_interactive_emits_stage_labels(monkeypatch):
    """Force the TTY branch and verify the spinner runs without crashing."""
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)

    buffer = io.StringIO()
    recorded = Console(
        file=buffer,
        width=120,
        force_terminal=True,
        color_system=None,
    )
    monkeypatch.setattr(formatter, "console", recorded)

    # Shrink the stage timings so the test stays fast.
    monkeypatch.setattr(formatter, "_STAGE_DURATIONS_S", [0.01, 0.01])

    with formatter.with_progress(stages=["Step one", "Step two"]):
        pass

    output = buffer.getvalue()
    # The progress widget redraws in-place, but the final state must contain
    # the "Analysis complete" label we write in the finally block.
    assert "Analysis complete" in output


def test_render_health_check_silent_on_ok(monkeypatch):
    buffer = io.StringIO()
    recorded = Console(file=buffer, width=80, force_terminal=False, color_system=None)
    monkeypatch.setattr(formatter, "error_console", recorded)

    formatter.render_health_check("http://x", ok=True)
    assert buffer.getvalue() == ""


def test_render_health_check_prints_on_failure(monkeypatch):
    buffer = io.StringIO()
    recorded = Console(file=buffer, width=80, force_terminal=False, color_system=None)
    monkeypatch.setattr(formatter, "error_console", recorded)

    formatter.render_health_check("http://x", ok=False)
    assert "http://x" in buffer.getvalue()


def test_render_request_summary_shows_pr_and_repo(monkeypatch):
    buffer = io.StringIO()
    recorded = Console(file=buffer, width=120, force_terminal=False, color_system=None)
    monkeypatch.setattr(formatter, "console", recorded)

    formatter.render_request_summary("pr-142", "https://github.com/x/y")
    output = buffer.getvalue()
    assert "pr-142" in output
    assert "https://github.com/x/y" in output
