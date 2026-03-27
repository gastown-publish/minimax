"""HTTP server mode with /health endpoint for monitoring."""

from __future__ import annotations

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Any

import click

from .. import __version__
from ..api import check_health
from ..constants import DEFAULT_MODEL

# Server start time for uptime calculation
_START_TIME = time.time()


__all__ = ["_get_health_data", "cmd", "http"]
def _get_health_data() -> dict[str, Any]:
    """Build health check response data."""
    # Check backend API health
    api_healthy = check_health(timeout=2)

    return {
        "status": "healthy" if api_healthy else "degraded",
        "version": __version__,
        "uptime_seconds": int(time.time() - _START_TIME),
        "model": {
            "id": DEFAULT_MODEL,
            "backend_healthy": api_healthy,
        },
    }


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP request handler with /health endpoint."""

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default logging."""
        pass

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/health":
            self._send_health()
        elif self.path == "/":
            self._send_root()
        else:
            self._send_not_found()

    def _send_health(self) -> None:
        """Send /health response."""
        data = _get_health_data()
        response = json.dumps(data, indent=2)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response.encode())

    def _send_root(self) -> None:
        """Send root response."""
        response = json.dumps({
            "service": "mm",
            "version": __version__,
            "endpoints": ["/health"],
        }, indent=2)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response.encode())

    def _send_not_found(self) -> None:
        """Send 404 response."""
        response = json.dumps({"error": "Not found"})
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response.encode())


@click.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to.")
@click.option("--port", default=8080, type=int, help="Port to listen on.")
def http(host: str, port: int):
    """Start HTTP server with /health endpoint for monitoring.

    The server provides:
    - GET /health - Health check with status, version, uptime, and model info
    - GET / - Service info

    Example:
        mm http --port 8080
    """
    server = HTTPServer((host, port), HealthHandler)

    click.echo(f"Starting mm HTTP server on {host}:{port}")
    click.echo(f"  GET /health - Health check")
    click.echo(f"  GET /      - Service info")
    click.echo(f"Press Ctrl+C to stop")

    # Run server in background thread so click doesn't block
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nShutting down...")
        server.shutdown()