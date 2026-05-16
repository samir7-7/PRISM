"""Typed exceptions for the PRISM CLI.

Every error carries a one-line ``hint`` describing the most likely fix.
``main.py`` has a single top-level ``except PrismError`` that routes the error
to ``formatter.render_error`` and exits with a non-zero code.
"""

from __future__ import annotations


class PrismError(Exception):
    """Base class for every CLI-surfaced error.

    Sub-classes set a default ``hint`` that the formatter prints below the
    error message — keep it actionable, one line, no marketing.
    """

    default_hint: str = ""

    def __init__(self, message: str, *, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint if hint is not None else self.default_hint

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


class BackendUnreachable(PrismError):
    """The CLI could not establish a TCP connection to the backend."""

    default_hint = "is the backend running? Try `uvicorn backend.main:app --reload`."


class BackendTimeout(PrismError):
    """The backend accepted the connection but did not respond in time."""

    default_hint = "the backend may be overloaded or the PR is very large - try again."


class BackendBadRequest(PrismError):
    """The backend rejected the request payload (4xx other than 401/404)."""

    default_hint = "check the PR identifier and repository URL."


class BackendServerError(PrismError):
    """The backend hit a 5xx — analysis pipeline failure."""

    default_hint = "check backend logs; retry once the service recovers."


class AuthError(PrismError):
    """GitHub authentication failed (401)."""

    default_hint = "check your PRISM_GITHUB_TOKEN in .env (or --token)."


class NotFoundError(PrismError):
    """PR or repository was not found (404)."""

    default_hint = "verify the repository URL and that the PR number exists."


class ConfigError(PrismError):
    """Required configuration was not supplied."""

    default_hint = "pass the missing flag or set the env var in .env."


class ValidationError(PrismError):
    """Backend response validation failed (shape mismatch)."""

    default_hint = "backend may be returning unexpected data - check backend version."
