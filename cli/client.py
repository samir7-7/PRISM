"""HTTP client for the PRISM backend.

One method does real work — ``AnalysisClient.run`` POSTs a single JSON body
to ``/api/analysis/run`` and validates the response. ``check_health`` is a
cheap pre-flight ping that lets us fail fast on a wrong backend URL before
burning 25 seconds on the real analysis call.
"""

from __future__ import annotations

from typing import Literal

import httpx
from pydantic import BaseModel, Field, ValidationError

from .errors import (
    AuthError,
    BackendBadRequest,
    BackendServerError,
    BackendTimeout,
    BackendUnreachable,
    NotFoundError,
)


class AnalysisResponse(BaseModel):
    """Mirrors the backend ``AnalysisResponse`` schema (frozen contract)."""

    report_id: str
    dashboard_url: str
    risk_score: int = Field(..., ge=0, le=100, description="Risk score (0-100)")
    risk_label: Literal["LOW", "MEDIUM", "HIGH"]
    impacted_node_count: int = Field(..., ge=0, description="Number of impacted nodes")
    status: Literal["COMPLETE", "PARTIAL"]


class AnalysisClient:
    """Thin synchronous wrapper around ``httpx.Client``.

    Constructed once per CLI invocation. ``transport`` is exposed so tests
    can swap in ``httpx.MockTransport`` without monkey-patching.
    """

    def __init__(
        self,
        backend_url: str,
        timeout: float = 60.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.backend_url = backend_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout, transport=transport)

    # ------------------------------------------------------------------ #
    # Health
    # ------------------------------------------------------------------ #
    def check_health(self) -> bool:
        """Return ``True`` iff ``GET /healthz`` answers 200 ``{"ok": true}``.

        Any network/HTTP failure returns ``False`` rather than raising — the
        caller turns that into a ``BackendUnreachable`` with a helpful hint.
        """
        try:
            response = self._client.get(f"{self.backend_url}/healthz", timeout=2.0)
        except (httpx.ConnectError, httpx.TimeoutException, httpx.TransportError):
            return False
        if response.status_code != 200:
            return False
        try:
            return bool(response.json().get("ok"))
        except ValueError:
            return False

    # ------------------------------------------------------------------ #
    # Analysis
    # ------------------------------------------------------------------ #
    def run(
        self,
        pr_identifier: str,
        repository_url: str,
        github_token: str | None = None,
    ) -> AnalysisResponse:
        """Submit one analysis request and return the parsed response.

        Raises a typed ``PrismError`` sub-class on every failure path so the
        top-level handler in ``main.py`` can render a single nice error box.
        """
        payload: dict[str, str] = {
            "pr_identifier": pr_identifier,
            "repository_url": repository_url,
        }
        if github_token:
            payload["github_token"] = github_token

        url = f"{self.backend_url}/api/analysis/run"

        try:
            response = self._client.post(url, json=payload)
        except httpx.ConnectError as exc:
            raise BackendUnreachable(f"Cannot reach PRISM backend at {self.backend_url}") from exc
        except httpx.TimeoutException as exc:
            raise BackendTimeout(f"Analysis timed out after {self.timeout:g}s") from exc
        except httpx.TransportError as exc:
            raise BackendUnreachable(f"Network error talking to {self.backend_url}: {exc}") from exc

        if response.status_code == 200:
            try:
                return AnalysisResponse(**response.json())
            except (ValidationError, ValueError) as exc:
                raise BackendServerError(
                    "Backend returned an unexpected response shape",
                    hint="check that the backend version matches the CLI contract.",
                ) from exc

        # Map HTTP error → typed PrismError with the backend's `detail` text.
        detail = _extract_detail(response)
        status = response.status_code

        if status == 401:
            raise AuthError(detail or "GitHub authentication failed")
        if status == 404:
            raise NotFoundError(detail or "Pull request or repository not found")
        if 400 <= status < 500:
            raise BackendBadRequest(detail or f"Backend rejected request ({status})")
        raise BackendServerError(detail or f"Backend error ({status})")

    # ------------------------------------------------------------------ #
    # Context manager (so `with AnalysisClient(...) as c:` works in tests)
    # ------------------------------------------------------------------ #
    def __enter__(self) -> "AnalysisClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self._client.close()

    def close(self) -> None:
        self._client.close()


def _extract_detail(response: httpx.Response) -> str:
    """Pull a human-readable error message out of a FastAPI error response.

    Handles both the simple ``{"detail": "..."}`` shape and the 422 list shape
    (``{"detail": [{"loc": [...], "msg": "...", ...}]}``).
    """
    try:
        body = response.json()
    except ValueError:
        return response.text.strip()[:200]

    detail = body.get("detail") if isinstance(body, dict) else None
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail:
        first = detail[0]
        if isinstance(first, dict) and "msg" in first:
            loc = ".".join(str(p) for p in first.get("loc", []) if p != "body")
            msg = first["msg"]
            return f"{loc}: {msg}" if loc else msg
    return ""
