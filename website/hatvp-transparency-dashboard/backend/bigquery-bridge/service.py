"""Authentication, BigQuery execution, and dashboard slice conversion."""

from __future__ import annotations

import hmac
import json
import os
from typing import Any

from query import TABLES, build_query


def response(payload: dict[str, Any], status: int) -> tuple[str, int, dict[str, str]]:
    """Return a framework-compatible JSON response without internal details."""

    return (
        json.dumps(payload, separators=(",", ":"), default=str),
        status,
        {"Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store"},
    )


def error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


def row_value(row: Any, key: str) -> Any:
    try:
        return row[key]
    except (KeyError, TypeError, AttributeError):
        return getattr(row, key)


def parse_array(raw: Any) -> list[dict[str, Any]]:
    value = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(value, list):
        raise ValueError("BigQuery returned an invalid aggregate array")
    return [item for item in value if isinstance(item, dict)]


def normalize_breakdown(items: list[dict[str, Any]], include_total: bool) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in items:
        normalized: dict[str, Any] = {
            "label": str(item.get("label", "unknown")),
            "rows": int(item.get("row_count", 0)),
        }
        if include_total:
            normalized["totalValue"] = float(item.get("total_value", 0) or 0)
        result.append(normalized)
    return result


def dashboard_payload(row: Any, view: str) -> dict[str, Any]:
    """Convert one independent query row to the public slice contract."""

    payload = {
        "snapshotDate": row_value(row, "snapshot_date"),
        "generatedAt": str(row_value(row, "generated_at")),
    }
    if view == "overview":
        table_items = parse_array(row_value(row, "tables_json"))
        tables = {str(item["table_name"]): int(item["row_count"]) for item in table_items}
        payload["tables"] = {name: tables.get(name, 0) for name in TABLES}
        return payload
    payload["items"] = normalize_breakdown(
        parse_array(row_value(row, "items_json")), view != "declarations"
    )
    return payload


def authorized(request: Any, expected: str) -> bool:
    supplied = request.headers.get("Authorization", "")
    return bool(expected) and hmac.compare_digest(supplied, f"Bearer {expected}")


def client() -> Any:
    from google.cloud import bigquery

    return bigquery.Client(project=os.environ["BQ_PROJECT_ID"])


def run_dashboard(view: str = "overview") -> tuple[str, int, dict[str, str]]:
    """Execute one fixed slice query and convert its single result row."""

    try:
        project = os.environ["BQ_PROJECT_ID"]
        dataset = os.environ["BQ_DATASET"]
        query_job = client().query(
            build_query(project, dataset, view), location=os.environ.get("BQ_LOCATION")
        )
        rows = list(query_job.result())
        if not rows or row_value(rows[0], "snapshot_date") is None:
            return response(error_payload("NO_DATA", "No dashboard snapshot is available"), 404)
        return response(dashboard_payload(rows[0], view), 200)
    except Exception:
        return response(error_payload("QUERY_FAILED", "Dashboard data is unavailable"), 502)
