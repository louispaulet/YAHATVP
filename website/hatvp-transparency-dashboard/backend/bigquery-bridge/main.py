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

from bridge_runtime import authorized, error_payload, response
from service import (
    run_age_analysis,
    run_dashboard,
    run_declaration,
    run_search,
    run_simple_analysis,
)

SLICE_ROUTES = {
    "/v1/dashboard/overview": "overview",
    "/v1/dashboard/income": "income",
    "/v1/dashboard/assets": "assets",
    "/v1/dashboard/declarations": "declarations",
    "/v1/dashboard/gender": "gender",
    "/v1/dashboard/search": "search",
    "/v1/dashboard/simple-analysis": "simple-analysis",
    "/v1/dashboard/age-analysis": "age-analysis",
}
DECLARATION_ROUTE_PREFIX = "/v1/dashboard/declarations/"


def not_found() -> tuple[str, int, dict[str, str]]:
    return response(error_payload("NOT_FOUND", "Route not found"), 404)


def method_not_allowed() -> tuple[str, int, dict[str, str]]:
    return response(error_payload("METHOD_NOT_ALLOWED", "Use GET for dashboard data"), 405)


def health() -> tuple[str, int, dict[str, str]]:
    return response({"ok": True}, 200)


def is_health_request(request: Any) -> bool:
    return request.path == "/healthz" and request.method == "GET"


def dashboard_view(request: Any) -> str | None:
    """Return the fixed query view for a public dashboard slice."""

    if request.path.startswith(DECLARATION_ROUTE_PREFIX):
        return "declaration"
    return SLICE_ROUTES.get(request.path)


def is_dashboard_request(request: Any) -> bool:
    """Identify a supported data route before checking method and credentials."""

    return dashboard_view(request) is not None


def declaration_uuid(request: Any) -> str:
    return request.path.removeprefix(DECLARATION_ROUTE_PREFIX).strip()


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
    if dashboard_view(request) == "search":
        search_term = str(getattr(request, "args", {}).get("q", "")).strip()
        if not search_term:
            return response(error_payload("INVALID_QUERY", "Enter a search term"), 400)
        if len(search_term) > 120:
            return response(error_payload("INVALID_QUERY", "Search term is too long"), 400)
        return run_search(search_term)
    if dashboard_view(request) == "age-analysis":
        search_term = str(getattr(request, "args", {}).get("q", "")).strip()
        if not search_term:
            return response(error_payload("INVALID_QUERY", "Enter a declarant name"), 400)
        if len(search_term) > 120:
            return response(error_payload("INVALID_QUERY", "Search term is too long"), 400)
        return run_age_analysis(search_term)
    if dashboard_view(request) == "simple-analysis":
        return run_simple_analysis()
    if dashboard_view(request) == "declaration":
        identifier = declaration_uuid(request)
        if not identifier or "/" in identifier or len(identifier) > 120:
            return response(error_payload("INVALID_QUERY", "Invalid declaration identifier"), 400)
        return run_declaration(identifier)
    return run_dashboard(dashboard_view(request) or "overview")


@functions_framework.http
def dashboard(request: Any) -> tuple[str, int, dict[str, str]]:
    """Serve health, aggregate slices, and public declaration search."""

    return dashboard_route(request)
