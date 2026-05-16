"""Edge cases for ``cli.client`` not covered by happy-path/error-mapping tests."""

from __future__ import annotations

import httpx
import pytest

from cli.errors import BackendBadRequest, BackendServerError, BackendTimeout, BackendUnreachable

from .conftest import make_client


def test_run_maps_timeout_exception_to_backend_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow")

    client = make_client(handler)
    with pytest.raises(BackendTimeout):
        client.run("pr-1", "https://github.com/x/y")


def test_run_maps_other_transport_errors_to_unreachable():
    def handler(request: httpx.Request) -> httpx.Response:
        # ProtocolError is a TransportError sub-class but not ConnectError /
        # TimeoutException — exercises the fall-through branch.
        raise httpx.ProtocolError("broken pipe")

    client = make_client(handler)
    with pytest.raises(BackendUnreachable):
        client.run("pr-1", "https://github.com/x/y")


def test_run_error_without_detail_uses_default_message():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={})

    client = make_client(handler)
    with pytest.raises(BackendBadRequest) as exc:
        client.run("pr-1", "https://github.com/x/y")
    assert "400" in str(exc.value)


def test_run_non_json_error_body_falls_back_to_text():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, content=b"raw server crash text")

    client = make_client(handler)
    with pytest.raises(BackendServerError) as exc:
        client.run("pr-1", "https://github.com/x/y")
    assert "raw server crash text" in str(exc.value)


def test_check_health_returns_false_when_ok_field_missing():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "alive"})

    client = make_client(handler)
    assert client.check_health() is False


def test_check_health_returns_false_when_body_not_json():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    client = make_client(handler)
    assert client.check_health() is False


def test_client_works_as_context_manager():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/healthz":
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(200, json={"ok": True})

    with make_client(handler) as client:
        assert client.check_health() is True


def test_client_strips_trailing_slash_from_backend_url():
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    from cli.client import AnalysisClient

    client = AnalysisClient(backend_url="http://test/", transport=transport)
    client.check_health()
    assert captured["url"] == "http://test/healthz"
