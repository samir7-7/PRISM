"""Tests for ``cli.client``: request shape, response parsing, error mapping."""

from __future__ import annotations

import httpx
import pytest

from cli.client import AnalysisResponse
from cli.errors import (
    AuthError,
    BackendBadRequest,
    BackendServerError,
    BackendUnreachable,
    NotFoundError,
)

from .conftest import SUCCESS_BODY, make_client


# --------------------------------------------------------------------- #
# Happy path
# --------------------------------------------------------------------- #
def test_run_posts_expected_payload_and_parses_response():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["method"] = request.method
        captured["body"] = request.content
        return httpx.Response(200, json=SUCCESS_BODY)

    client = make_client(handler)
    response = client.run(
        pr_identifier="pr-142",
        repository_url="https://github.com/owner/repo",
        github_token="ghp_xxx",
    )

    assert isinstance(response, AnalysisResponse)
    assert response.risk_score == 50
    assert response.risk_label == "MEDIUM"
    assert captured["method"] == "POST"
    assert captured["url"] == "http://test/api/analysis/run"

    import json

    sent = json.loads(captured["body"])
    assert sent == {
        "pr_identifier": "pr-142",
        "repository_url": "https://github.com/owner/repo",
        "github_token": "ghp_xxx",
    }


def test_run_omits_token_when_none():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.content
        return httpx.Response(200, json=SUCCESS_BODY)

    client = make_client(handler)
    client.run(pr_identifier="pr-1", repository_url="https://github.com/x/y")

    import json

    sent = json.loads(captured["body"])
    assert "github_token" not in sent


# --------------------------------------------------------------------- #
# Health
# --------------------------------------------------------------------- #
def test_check_health_returns_true_on_ok():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ok": True})

    client = make_client(handler)
    assert client.check_health() is True


def test_check_health_returns_false_on_404():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    client = make_client(handler)
    assert client.check_health() is False


def test_check_health_returns_false_on_connection_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("nope")

    client = make_client(handler)
    assert client.check_health() is False


# --------------------------------------------------------------------- #
# Error mapping
# --------------------------------------------------------------------- #
def test_run_maps_401_to_auth_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Bad credentials"})

    client = make_client(handler)
    with pytest.raises(AuthError) as exc:
        client.run("pr-1", "https://github.com/x/y")
    assert "Bad credentials" in str(exc.value)


def test_run_maps_404_to_not_found():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "PR not found"})

    client = make_client(handler)
    with pytest.raises(NotFoundError):
        client.run("pr-1", "https://github.com/x/y")


def test_run_maps_400_to_bad_request():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"detail": "Invalid"})

    client = make_client(handler)
    with pytest.raises(BackendBadRequest):
        client.run("pr-1", "https://github.com/x/y")


def test_run_maps_500_to_server_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "boom"})

    client = make_client(handler)
    with pytest.raises(BackendServerError):
        client.run("pr-1", "https://github.com/x/y")


def test_run_maps_connect_error_to_unreachable():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    client = make_client(handler)
    with pytest.raises(BackendUnreachable):
        client.run("pr-1", "https://github.com/x/y")


def test_run_validates_response_shape():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    client = make_client(handler)
    with pytest.raises(BackendServerError):
        client.run("pr-1", "https://github.com/x/y")


def test_run_handles_422_validation_list():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422,
            json={
                "detail": [
                    {
                        "loc": ["body", "pr_identifier"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        )

    client = make_client(handler)
    with pytest.raises(BackendBadRequest) as exc:
        client.run("", "https://github.com/x/y")
    assert "field required" in str(exc.value)
