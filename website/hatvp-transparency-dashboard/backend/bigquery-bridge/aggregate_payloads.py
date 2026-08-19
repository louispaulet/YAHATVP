"""Stable public response shapes for aggregate dashboard slices."""

from __future__ import annotations

import json
from typing import Any

from query_support import TABLES


def row_value(row: Any, key: str) -> Any:
    """Read a BigQuery row using either mapping or attribute access."""

    try:
        return row[key]
    except (KeyError, TypeError, AttributeError):
        return getattr(row, key)


def parse_array(raw: Any) -> list[dict[str, Any]]:
    """Parse a JSON aggregate and discard malformed non-object members."""

    value = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(value, list):
        raise ValueError("BigQuery returned an invalid aggregate array")
    return [item for item in value if isinstance(item, dict)]


def normalize_breakdown(items: list[dict[str, Any]], include_total: bool) -> list[dict[str, Any]]:
    """Convert BigQuery aggregate keys into the dashboard's camel-case shape."""

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
    """Convert an aggregate slice row to its public API payload."""

    payload = {
        "snapshotDate": row_value(row, "snapshot_date"),
        "generatedAt": str(row_value(row, "generated_at")),
    }
    if view == "overview":
        table_items = parse_array(row_value(row, "tables_json"))
        tables = {str(item["table_name"]): int(item["row_count"]) for item in table_items}
        payload["tables"] = {name: tables.get(name, 0) for name in TABLES}
        return payload
    if view == "gender":
        items = normalize_breakdown(parse_array(row_value(row, "gender_json")), False)
        payload["gender"] = items
        payload["unknownRows"] = sum(
            item["rows"] for item in items if item["label"] not in {"male", "female"}
        )
        payload["positions"] = normalize_gender_positions(
            parse_array(row_value(row, "positions_json"))
        )
        return payload
    payload["items"] = normalize_breakdown(
        parse_array(row_value(row, "items_json")), view != "declarations"
    )
    if view != "declarations":
        payload["totalValue"] = float(row_value(row, "total_value") or 0)
    if view == "income":
        payload["yearCount"] = int(row_value(row, "year_count") or 0)
    return payload


def normalize_gender_positions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert position-by-gender aggregates into a public chart contract."""

    positions: list[dict[str, Any]] = []
    for item in items:
        male = int(item.get("male_count", 0) or 0)
        female = int(item.get("female_count", 0) or 0)
        unknown = int(item.get("unknown_count", 0) or 0)
        positions.append(
            {
                "label": str(item.get("label", "unknown")),
                "male": male,
                "female": female,
                "unknown": unknown,
            }
        )
    return positions


def snapshot_payload(row: Any) -> dict[str, Any]:
    """Return shared snapshot metadata for payloads that add their own body."""

    return {
        "snapshotDate": row_value(row, "snapshot_date"),
        "generatedAt": str(row_value(row, "generated_at")),
    }


__all__ = [
    "dashboard_payload",
    "normalize_breakdown",
    "parse_array",
    "row_value",
    "snapshot_payload",
]
