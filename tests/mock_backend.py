"""Stdlib-only mock PRISM backend for end-to-end CLI testing.

Implements just enough of the API contract to exercise the CLI's real network
path. Run with::

    python -m tests.mock_backend [--port 8765] [--mode complete|partial|500|401|slow]

Endpoints:

* ``GET /healthz`` → ``{"ok": true}`` (always, unless mode=down).
* ``POST /api/analysis/run`` → a canned ``AnalysisResponse``, optionally
  delayed or with an injected error depending on ``--mode``.
"""

from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Event


def make_handler(mode: str, ready: Event) -> type[BaseHTTPRequestHandler]:
    """Return a handler class parameterised by the chosen response mode."""

    class Handler(BaseHTTPRequestHandler):
        # Silence the default access-log spam.
        def log_message(self, format: str, *args: object) -> None:  # noqa: A002, ARG002
            return

        # ----- GET /healthz ------------------------------------------- #
        def do_GET(self) -> None:  # noqa: N802 (stdlib API)
            if self.path == "/healthz":
                self._json(200, {"ok": True})
                return
            self._json(404, {"detail": "not found"})

        # ----- POST /api/analysis/run --------------------------------- #
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                self._json(400, {"detail": "invalid JSON body"})
                return

            if self.path != "/api/analysis/run":
                self._json(404, {"detail": "unknown endpoint"})
                return

            # Basic schema check — mirrors what the real backend enforces.
            missing = [k for k in ("pr_identifier", "repository_url") if k not in body]
            if missing:
                self._json(
                    422,
                    {
                        "detail": [
                            {
                                "loc": ["body", missing[0]],
                                "msg": "field required",
                                "type": "value_error.missing",
                            }
                        ]
                    },
                )
                return

            if mode == "slow":
                time.sleep(2.0)

            if mode == "401":
                self._json(401, {"detail": "GitHub authentication failed"})
                return
            if mode == "404":
                self._json(404, {"detail": "PR not found"})
                return
            if mode == "500":
                self._json(500, {"detail": "pipeline crashed"})
                return

            response: dict[str, object] = {
                "report_id": "demo-8sj2kd",
                "dashboard_url": "http://localhost:3000/report/demo-8sj2kd",
                "risk_score": 82,
                "risk_label": "HIGH",
                "impacted_node_count": 14,
                "status": "PARTIAL" if mode == "partial" else "COMPLETE",
            }
            self._json(200, response)

        # ----- Helpers ------------------------------------------------ #
        def _json(self, status: int, body: dict) -> None:
            payload = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    # Signal startup once the class is built. The actual readiness happens
    # when the server starts listening, but for the in-process fixture this
    # is good enough.
    ready.set()
    return Handler


def serve(host: str, port: int, mode: str) -> HTTPServer:
    """Construct (but do not start) an ``HTTPServer`` configured for ``mode``."""
    ready = Event()
    handler = make_handler(mode, ready)
    return HTTPServer((host, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--mode",
        default="complete",
        choices=["complete", "partial", "slow", "401", "404", "500"],
    )
    args = parser.parse_args()

    server = serve(args.host, args.port, args.mode)
    print(f"[mock] listening on http://{args.host}:{args.port} (mode={args.mode})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
