"""Typer entry point: ``prism analyze``, ``prism demo``, ``prism version``.

This file is intentionally thin — every command does the same three things:
build a ``Settings``, call ``AnalysisClient.run``, hand the result to the
formatter. All real work lives behind those two modules.
"""

from __future__ import annotations

import webbrowser

import typer

from . import __version__
from .client import AnalysisClient, AnalysisResponse
from .config import Settings
from .demo_fixture import DEMO_PR_ID, DEMO_REPO_URL
from .errors import ConfigError, PrismError
from .formatter import (
    render_error,
    render_error_json,
    render_json,
    render_request_summary,
    render_summary,
    with_progress,
)
from .utils import detect_git_remote
from typing import Optional

app = typer.Typer(
    name="prism",
    help="PRISM — Pull Request Intelligent Semantic Monitor.",
    add_completion=False,
    no_args_is_help=True,
)


# --------------------------------------------------------------------- #
# analyze
# --------------------------------------------------------------------- #
@app.command()
def analyze(
    pr_id: str = typer.Argument(..., metavar="PR_ID", help="PR identifier, e.g. pr-142 or 142."),
    repo: Optional[str] = typer.Option(
        None,
        "--repo",
        help="Repository URL (overrides PRISM_REPO_URL).",
    ),
    open_browser: bool = typer.Option(
        False,
        "--open",
        help="Open the dashboard in the default browser after analysis.",
    ),
    backend: Optional[str] = typer.Option(
        None,
        "--backend",
        help="Backend URL (overrides PRISM_BACKEND_URL).",
    ),
    token: Optional[str] = typer.Option(
        None,
        "--token",
        help="GitHub access token (overrides PRISM_GITHUB_TOKEN).",
    ),
    # ``--json`` is hidden from --help on purpose (see CLI_PLAN §4). Still
    # fully wired so judges asking about CI integration get a live answer.
    json_output: bool = typer.Option(
        False,
        "--json",
        hidden=True,
        help="Emit machine-readable JSON instead of the Rich summary.",
    ),
) -> None:
    """Analyze a pull request and print a risk summary."""
    settings = Settings()
    if backend:
        settings.backend_url = backend
    if token is not None:
        settings.github_token = token
    if repo:
        settings.repo_url = repo
    if json_output:
        settings.output_format = "json"
    if open_browser:
        settings.auto_open = True

    if not settings.repo_url:
        # Fall back to the current directory's git origin so running `prism
        # analyze pr-142` from inside a checked-out repo Just Works. The
        # detection helper never raises — it returns None on every failure
        # path (no git binary, no origin, unparseable URL, timeout).
        detected = detect_git_remote()
        if detected:
            settings.repo_url = detected
            # Suppress the chatter in --json mode; printing before the JSON
            # payload would break `jq` consumers.
            if settings.output_format != "json":
                typer.echo(f"Detected repo: {detected}")
        else:
            _fail(
                ConfigError(
                    "Missing repository URL",
                    hint=(
                        "pass --repo, set PRISM_REPO_URL, "
                        "or run inside a git repo with an `origin` remote."
                    ),
                ),
                json_mode=settings.output_format == "json",
            )
    assert settings.repo_url is not None
    _run(
        pr_identifier=pr_id,
        repository_url=settings.repo_url,
        github_token=settings.github_token,
        backend_url=settings.backend_url,
        timeout=settings.timeout,
        json_mode=settings.output_format == "json",
        open_browser=settings.auto_open,
    )


# --------------------------------------------------------------------- #
# demo
# --------------------------------------------------------------------- #
@app.command()
def demo(
    backend: Optional[str] = typer.Option(
        None,
        "--backend",
        help="Backend URL (overrides PRISM_BACKEND_URL).",
    ),
    token: Optional[str] = typer.Option(
        None,
        "--token",
        help="GitHub access token (rarely needed for demo mode).",
    ),
) -> None:
    """Run a canned, bulletproof demo against the baked fixture PR.

    Equivalent to ``prism analyze pr-142 --repo <fixture-repo> --open`` —
    intended as the live-demo parachute that always works.
    """
    settings = Settings()
    if backend:
        settings.backend_url = backend
    if token is not None:
        settings.github_token = token

    _run(
        pr_identifier=DEMO_PR_ID,
        repository_url=DEMO_REPO_URL,
        github_token=settings.github_token,
        backend_url=settings.backend_url,
        timeout=settings.timeout,
        json_mode=False,
        open_browser=True,
    )


# --------------------------------------------------------------------- #
# version
# --------------------------------------------------------------------- #
@app.command()
def version() -> None:
    """Print the CLI version."""
    typer.echo(f"prism {__version__}")


# --------------------------------------------------------------------- #
# backend (sub-app)
# --------------------------------------------------------------------- #
# The bundled local backend lives in the sibling ``backend`` package and is
# opt-in via the ``[backend]`` extras group. Wired in as a Typer sub-app so
# ``prism backend serve`` works under the existing ``prism`` console script
# without a second entry point.
backend_app = typer.Typer(
    name="backend",
    help="Run the optional bundled PRISM backend.",
    no_args_is_help=True,
)
app.add_typer(backend_app, name="backend")


@backend_app.command("serve")
def backend_serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Interface to bind on."),
    port: int = typer.Option(8000, "--port", help="Port to listen on."),
) -> None:
    """Start the bundled FastAPI backend.

    Requires the ``[backend]`` extras (``pip install -e '.[backend]'``).
    Imports are deferred so users without the extras can still run every
    other command — only this one needs FastAPI/uvicorn on the path.
    """
    try:
        import uvicorn

        from backend.app import app as fastapi_app
    except ImportError:
        _fail(
            ConfigError(
                "Backend extra not installed",
                hint="install with: pip install -e '.[backend]'",
            ),
            json_mode=False,
        )
        return

    typer.echo(f"PRISM backend listening on http://{host}:{port}")
    uvicorn.run(fastapi_app, host=host, port=port, log_level="info")


# --------------------------------------------------------------------- #
# Shared runner
# --------------------------------------------------------------------- #
def _run(
    *,
    pr_identifier: str,
    repository_url: str,
    github_token: str | None,
    backend_url: str,
    timeout: int,
    json_mode: bool,
    open_browser: bool,
) -> None:
    """Common analyze/demo flow: health-check → POST → render → open."""
    client = AnalysisClient(backend_url=backend_url, timeout=float(timeout))

    try:
        # Pre-flight: a 2s ping fails fast if the backend isn't up. The real
        # POST can take 25s — without this we'd burn the demo waiting on a
        # connection that was never going to succeed.
        if not client.check_health():
            from .errors import BackendUnreachable

            raise BackendUnreachable(f"Cannot reach PRISM backend at {backend_url}")

        if not json_mode:
            render_request_summary(pr_identifier, repository_url)

        # Run the analysis behind a staged spinner (only when interactive).
        response: AnalysisResponse
        if json_mode:
            response = client.run(pr_identifier, repository_url, github_token)
        else:
            with with_progress():
                response = client.run(pr_identifier, repository_url, github_token)

        # Render
        if json_mode:
            render_json(response)
        else:
            render_summary(response)

        # Optional auto-open
        if open_browser and not json_mode and response.dashboard_url:
            try:
                webbrowser.open(response.dashboard_url)
            except Exception:  # pragma: no cover - browser env is fickle
                # Browser failures shouldn't fail the command — the URL is
                # already printed for the user to click.
                pass

    except PrismError as err:
        _fail(err, json_mode=json_mode, client=client)
    finally:
        client.close()


def _fail(err: PrismError, *, json_mode: bool, client: AnalysisClient | None = None) -> None:
    """Render an error and exit with code 1."""
    if json_mode:
        render_error_json(err)
    else:
        render_error(err)
    if client is not None:
        client.close()
    raise typer.Exit(code=1)


# Allow ``python -m cli.main`` for development.
if __name__ == "__main__":  # pragma: no cover
    app()
