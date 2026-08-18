"""Small shared runtime primitives for the authenticated dashboard bridge."""

from __future__ import annotations

import hmac
import json
import os
from typing import Any


def runtime_setting(name: str, default: str | None = None) -> str | None:
    """Read one non-secret deployment setting with an optional default."""

    return os.environ.get(name, default)


def response_headers() -> dict[str, str]:
    """Return the bridge's intentionally non-cacheable JSON headers."""

    return {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
    }


def response(payload: dict[str, Any], status: int) -> tuple[str, int, dict[str, str]]:
    """Return a framework-compatible JSON response without internal details."""

    return json.dumps(payload, separators=(",", ":"), default=str), status, response_headers()


def error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    """Build the stable error envelope returned by all bridge routes."""

    return {"error": {"code": code, "message": message}}


def authorized(request: Any, expected: str) -> bool:
    """Check the shared Worker-to-bridge bearer token in constant time."""

    supplied = request.headers.get("Authorization", "")
    return bool(expected) and hmac.compare_digest(supplied, f"Bearer {expected}")


def storage_client() -> Any:
    """Create the ADC-backed client used only for immutable raw snapshots."""

    from google.cloud import storage

    return storage.Client(project=os.environ["BQ_PROJECT_ID"])


def configured_bucket() -> str:
    """Return the required raw-snapshot bucket or fail explicitly."""

    return os.environ["HATVP_BUCKET"]


def configured_prefix() -> str:
    """Return the normalized raw-snapshot object prefix."""

    return runtime_setting("HATVP_PREFIX", "hatvp") or "hatvp"


__all__ = [
    "authorized",
    "configured_bucket",
    "configured_prefix",
    "error_payload",
    "response",
    "runtime_setting",
    "storage_client",
]
