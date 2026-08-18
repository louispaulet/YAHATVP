"""Gold tables containing only the latest applicable declaration versions."""

from __future__ import annotations

import json
from typing import Any

from .gold_selection import latest_declaration_keys, selection_date

GOLD_TABLES = ("declarations", "people", "incomes", "assets")


def build_gold(
    silver_history: dict[str, list[dict[str, Any]]], registry: list[dict[str, Any]]
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    """Return latest-version Gold rows and registry lifecycle updates."""

    selected = latest_declaration_keys(silver_history.get("declarations", []))
    gold = {
        name: [
            _gold_row(row, row.get("bronze_record_key") in selected)
            for row in silver_history.get(name, [])
            if row.get("bronze_record_key") in selected
        ]
        for name in GOLD_TABLES
    }
    updated = [_registry_gold_state(row, selected) for row in registry]
    return gold, updated


def _gold_row(row: dict[str, Any], selected: bool) -> dict[str, Any]:
    copied = dict(row)
    copied["is_latest_declaration"] = selected
    copied["active_in_gold"] = selected and bool(row.get("anomaly_active"))
    if selected and row.get("anomaly_status") == "superseded":
        copied["active_in_gold"] = False
    return copied


def _registry_gold_state(row: dict[str, Any], selected: set[str]) -> dict[str, Any]:
    updated = dict(row)
    evidence = _evidence(row.get("evidence"))
    reference = evidence.get("record_ref")
    latest = any(reference == f"{name}:{key}" for name in GOLD_TABLES for key in selected)
    updated["is_latest_declaration"] = latest
    updated["active_in_gold"] = latest and row.get("status") not in {"superseded", "resolved"}
    if not latest and row.get("status") == "active":
        updated["status"] = "superseded"
        updated["superseded_by"] = next(iter(selected), None)
    updated["metric_eligible"] = latest and bool(row.get("metric_eligible", False))
    return updated


def _evidence(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return value if isinstance(value, dict) else {}


def gold_metric_rows(
    tables: dict[str, list[dict[str, Any]]], field: str = "normalized_value"
) -> list[dict[str, Any]]:
    """Return Gold rows eligible for a named metric without correcting values."""

    return [
        row
        for rows in tables.values()
        for row in rows
        if row.get("active_in_gold") is not False
        and json.loads(row.get("field_metric_eligibility_json") or "{}").get(field, True)
    ]


__all__ = [
    "GOLD_TABLES",
    "build_gold",
    "gold_metric_rows",
    "latest_declaration_keys",
    "selection_date",
]
