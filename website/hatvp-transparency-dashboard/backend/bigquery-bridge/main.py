"""Cloud Run Functions Framework entrypoint for the dashboard bridge."""

from __future__ import annotations

import os
from typing import Any

try:
    import functions_framework
except ImportError:  # pragma: no cover - fixture-only repository tests use the fallback

    class _FunctionsFramework:
        @staticmethod
        def http(function: Any) -> Any:
            return function

    functions_framework = _FunctionsFramework()

from service import authorized, error_payload, response, run_dashboard


def not_found() -> tuple[str, int, dict[str, str]]:
    """Return a generic response for paths outside the bridge contract."""

    return response(error_payload("NOT_FOUND", "Route not found"), 404)


def method_not_allowed() -> tuple[str, int, dict[str, str]]:
    """Keep methods explicit so accidental write routes never reach BigQuery."""

    return response(error_payload("METHOD_NOT_ALLOWED", "Use GET for dashboard data"), 405)


def health() -> tuple[str, int, dict[str, str]]:
    """Provide a dependency-free probe for Cloud Run health checks."""

    return response({"ok": True}, 200)


def is_health_request(request: Any) -> bool:
    """Keep the health route independent from BigQuery configuration."""

    return request.path == "/healthz" and request.method == "GET"


def is_dashboard_request(request: Any) -> bool:
    """Identify the sole data route before checking method and credentials."""

    # Keeping this predicate separate makes the public route inventory obvious.

    return request.path == "/v1/dashboard"


def dashboard_route(request: Any) -> tuple[str, int, dict[str, str]]:
    """Route one request after the framework has provided its HTTP object."""

    if is_health_request(request):
        return health()
    if not is_dashboard_request(request):
        return not_found()
    if request.method != "GET":
        return method_not_allowed()
    if not authorized(request, os.environ.get("BRIDGE_TOKEN", "")):
        return response(error_payload("UNAUTHORIZED", "Unauthorized"), 401)
    return run_dashboard()


@functions_framework.http
def dashboard(request: Any) -> tuple[str, int, dict[str, str]]:
    """Serve only health and aggregate dashboard endpoints."""

    return dashboard_route(request)
