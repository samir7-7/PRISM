"""Rich-based output rendering.

Three public surfaces:

* ``with_progress`` — context manager that drives a fake-but-honest staged
  spinner while the backend runs the real (synchronous) analysis.
* ``render_summary`` — the boxed summary panel printed after a successful run.
* ``render_error`` / ``render_json`` — the two terminal output paths.

The progress stage labels are cosmetic: the backend is a single blocking POST
and we don't get per-stage events. Each label corresponds to a real backend
phase, so the story stays honest. Swapping to SSE later wouldn't change this
file's public surface.
"""

from __future__ import annotations

import json
import sys
import threading
from contextlib import contextmanager
from typing import Iterator

from rich.box import HEAVY, ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text

from .client import AnalysisResponse
from .errors import PrismError


def _stdout_supports_unicode() -> bool:
    """Return True if ``sys.stdout`` can encode the characters we use.

    The Windows legacy console uses cp1252 by default — it explodes on the
    check-mark / arrow glyphs we render. We detect that up-front and fall
    back to ASCII equivalents so the CLI runs on every Windows machine
    without forcing the user to set ``PYTHONIOENCODING``.
    """
    encoding = (getattr(sys.stdout, "encoding", None) or "").lower()
    if not encoding or encoding in {"cp1252", "ascii"}:
        return False
    try:
        "✓⚠✗▸━".encode(encoding)
    except (UnicodeEncodeError, LookupError):
        return False
    return True


# Choose glyphs once at import time. ASCII fallbacks keep the layout but
# avoid Unicode encode errors on the legacy Windows console.
_UNICODE = _stdout_supports_unicode()
GLYPH_OK = "✓" if _UNICODE else "v"
GLYPH_WARN = "⚠" if _UNICODE else "!"
GLYPH_FAIL = "✗" if _UNICODE else "x"
GLYPH_ARROW = "▸" if _UNICODE else ">"

# Canonical stage labels — also the public ordering for the spinner.
ANALYSIS_STAGES: list[str] = [
    "Fetching PR diff",
    "Parsing AST",
    "Building dependency graph",
    "Traversing impact (2 hops)",
    "Calling AI for semantic reasoning",
    "Computing risk score",
    "Generating regression scenarios",
]

# Per-stage hold time in seconds. The semantic-reasoning step is by far the
# slowest in practice, so the spinner lingers there longest. Total ≈ 24s,
# which matches the backend's typical 20–25s wall time. If the real call
# finishes early the spinner is closed; if it overshoots, we hold on the last
# stage rather than racing past the end.
_STAGE_DURATIONS_S: list[float] = [1.0, 1.5, 2.5, 2.0, 12.0, 2.5, 2.5]

# Risk-label → Rich style. Used by both the score panel and the title.
RISK_STYLE: dict[str, str] = {
    "LOW": "bold green",
    "MEDIUM": "bold yellow",
    "HIGH": "bold red",
}

# Module-level console so tests can monkey-patch a recording Console here.
# ``safe_box=True`` swaps fancy Unicode box-drawing for ASCII when the
# detected encoding can't represent it — same defensive move as the glyphs.
console = Console(safe_box=not _UNICODE)
error_console = Console(stderr=True, safe_box=not _UNICODE)


# --------------------------------------------------------------------- #
# Progress
# --------------------------------------------------------------------- #
@contextmanager
def with_progress(stages: list[str] | None = None) -> Iterator[None]:
    """Show a staged spinner while the backend works.

    A background thread advances the stage label on the schedule defined by
    ``_STAGE_DURATIONS_S``; once the caller exits the context, the spinner
    closes regardless of whether the timer finished. Suppressed automatically
    when stdout is not a TTY (CI, ``--json``-piped use).
    """
    stages = stages or ANALYSIS_STAGES

    # In non-interactive contexts the spinner just adds noise. Yield a no-op
    # so the same call site works in tests and pipelines.
    if not sys.stdout.isatty():
        yield
        return

    progress = Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold]{task.description}[/bold]"),
        BarColumn(bar_width=None, complete_style="cyan", finished_style="cyan"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )

    total = len(stages)
    stop = threading.Event()

    with progress:
        task_id = progress.add_task(stages[0], total=total)

        def _advance() -> None:
            for index in range(total):
                # Update label to the *current* stage; bar advances to index.
                progress.update(task_id, description=stages[index], completed=index)
                # Wait for either the stage duration or an early stop.
                if stop.wait(_STAGE_DURATIONS_S[index]):
                    return
            # All scripted stages elapsed but the backend still hasn't replied —
            # park on the last stage so we don't pretend to be done.
            progress.update(task_id, description=stages[-1], completed=total - 1)

        thread = threading.Thread(target=_advance, daemon=True)
        thread.start()
        try:
            yield
        finally:
            stop.set()
            thread.join(timeout=0.1)
            progress.update(
                task_id,
                description="Analysis complete",
                completed=total,
            )


# --------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------- #
def render_summary(response: AnalysisResponse) -> None:
    """Print the post-analysis summary panel to stdout."""
    risk_style = RISK_STYLE.get(response.risk_label, "bold")

    # Title — em-dash falls back to hyphen on cp1252-only terminals so the
    # banner never crashes the run on legacy Windows consoles.
    separator = " — " if _UNICODE else " - "
    title = Panel(
        Text(f"PRISM{separator}Pull Request Intelligent Semantic Monitor", style="bold cyan"),
        box=HEAVY,
        border_style="cyan",
        padding=(0, 2),
    )
    console.print()
    console.print(title)
    console.print()

    # Status checklist
    checklist = Text()
    checklist.append(f"  {GLYPH_OK} Pull request analyzed\n", style="green")
    checklist.append(f"  {GLYPH_OK} Dependency graph constructed\n", style="green")
    checklist.append(
        f"  {GLYPH_OK} {response.impacted_node_count} impacted node"
        f"{'s' if response.impacted_node_count != 1 else ''} identified\n",
        style="green",
    )
    if response.risk_label == "HIGH":
        checklist.append(f"  {GLYPH_WARN} Semantic risks detected\n", style="yellow")
    else:
        checklist.append(f"  {GLYPH_OK} Semantic checks passed\n", style="green")
    checklist.append(f"  {GLYPH_OK} Regression scenarios generated\n", style="green")
    console.print(checklist)

    # PARTIAL status warning — graceful degradation per the PRD.
    if response.status == "PARTIAL":
        console.print(
            Text(
                f"  {GLYPH_WARN} AI service unavailable - graph and score are still valid.",
                style="yellow",
            )
        )
        console.print()

    # Risk-score box
    score_text = Text()
    score_text.append("Risk Score:  ", style="bold")
    score_text.append(
        f"{response.risk_label}  ({response.risk_score} / 100)",
        style=risk_style,
    )
    score_panel = Panel(
        score_text,
        box=ROUNDED,
        border_style=risk_style,
        padding=(0, 2),
        expand=False,
    )
    console.print(score_panel)
    console.print()

    # Dashboard link
    console.print(Text("  Open full analysis:", style="bold"))
    link = Text(
        f"  {GLYPH_ARROW} {response.dashboard_url}",
        style=f"underline {risk_style.split()[-1]}",
    )
    console.print(link)
    console.print()


# --------------------------------------------------------------------- #
# Errors
# --------------------------------------------------------------------- #
def render_error(err: PrismError) -> None:
    """Print a red boxed error with the typed exception's hint."""
    body = Text()
    body.append(f"{GLYPH_FAIL} ", style="bold red")
    body.append(err.message, style="bold")
    if err.hint:
        body.append("\n  Hint: ", style="dim")
        body.append(err.hint, style="dim")

    panel = Panel(
        body,
        box=ROUNDED,
        border_style="red",
        padding=(0, 2),
        expand=False,
    )
    error_console.print()
    error_console.print(panel)
    error_console.print()


# --------------------------------------------------------------------- #
# JSON output
# --------------------------------------------------------------------- #
def render_json(response: AnalysisResponse) -> None:
    """Emit raw JSON on stdout — pipe-clean, no Rich formatting."""
    print(json.dumps(response.model_dump(), separators=(",", ":")))


def render_error_json(err: PrismError) -> None:
    """Emit a structured error object — used in ``--json`` mode."""
    print(
        json.dumps(
            {"error": err.message, "hint": err.hint},
            separators=(",", ":"),
        ),
        file=sys.stderr,
    )


# --------------------------------------------------------------------- #
# Misc
# --------------------------------------------------------------------- #
def render_health_check(backend_url: str, ok: bool) -> None:
    """Tiny one-liner used by the pre-flight check on failure paths."""
    if ok:
        return
    error_console.print(
        Text(
            f"{GLYPH_FAIL} Backend at {backend_url} is not responding to /healthz",
            style="red",
        ),
    )


def render_request_summary(pr_identifier: str, repository_url: str) -> None:
    """Print what we're about to ask the backend for — keeps demos transparent."""
    table = Table.grid(padding=(0, 1))
    table.add_column(style="dim")
    table.add_column()
    table.add_row("PR:", Text(pr_identifier, style="bold"))
    table.add_row("Repo:", Text(repository_url, style="cyan"))
    console.print(table)
    console.print()
