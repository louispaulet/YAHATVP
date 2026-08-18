"""Silver construction: source-preserving rows plus anomaly metadata."""

from __future__ import annotations

import json
from typing import Any

import polars as pl

from .anomaly import detect_anomalies, parent_map, record_ref
from .registry import upsert_registry
from .silver_metadata import annotate_tables, occurrences_by_ref

SILVER_TABLES = ("declarations", "people", "incomes", "assets")
SILVER_FIELDS = {
    "declarant_key": pl.String,
    "anomaly_status": pl.String,
    "anomaly_rule_ids": pl.String,
    "anomaly_registry_ids": pl.String,
    "anomaly_evidence_json": pl.String,
    "field_metric_eligibility_json": pl.String,
    "metric_eligible": pl.Boolean,
    "anomaly_active": pl.Boolean,
    "previously_reported": pl.Boolean,
    "is_latest_declaration": pl.Boolean,
    "active_in_gold": pl.Boolean,
    "superseded_by": pl.String,
}


def build_silver(
    current: dict[str, list[dict[str, Any]]],
    history: dict[str, list[dict[str, Any]]] | None = None,
    registry: list[dict[str, Any]] | None = None,
    snapshot_date: str | None = None,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    """Return current Silver, full historical Silver context, and registry rows."""

    history = history or {}
    combined = {name: [*history.get(name, []), *current.get(name, [])] for name in SILVER_TABLES}
    occurrences = detect_anomalies(current, history, registry)
    current_refs = {
        record_ref(name, row) for name in SILVER_TABLES for row in current.get(name, [])
    }
    current_occurrences = [item for item in occurrences if item["record_ref"] in current_refs]
    snapshot = snapshot_date or _snapshot(current)
    registry_rows = upsert_registry(current_occurrences, registry or [], snapshot)
    by_ref = occurrences_by_ref(occurrences, {row["anomaly_key"]: row for row in registry_rows})
    all_silver = annotate_tables(combined, parent_map(combined), by_ref)
    current_silver = {
        name: [row for row in all_silver[name] if str(row.get("snapshot_date")) == snapshot]
        for name in SILVER_TABLES
    }
    return current_silver, all_silver, registry_rows


def apply_registry_states(
    tables: dict[str, list[dict[str, Any]]], registry: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    """Carry Gold lifecycle decisions back to the current Silver partition."""

    states = {row.get("anomaly_id"): row for row in registry if row.get("anomaly_id")}
    return {name: [_apply_state(row, states) for row in rows] for name, rows in tables.items()}


def _apply_state(row: dict[str, Any], states: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ids = json.loads(row.get("anomaly_registry_ids") or "[]")
    matches = [states[identifier] for identifier in ids if identifier in states]
    copied = dict(row)
    if any(item.get("status") == "regression" for item in matches):
        copied["anomaly_status"], copied["anomaly_active"] = "regression", True
    elif matches and all(item.get("status") in {"superseded", "resolved"} for item in matches):
        copied["anomaly_status"], copied["anomaly_active"] = "superseded", False
        copied["active_in_gold"] = False
        copied["superseded_by"] = next(
            (item.get("superseded_by") for item in matches if item.get("superseded_by")), None
        )
    return copied


def _snapshot(tables: dict[str, list[dict[str, Any]]]) -> str:
    for rows in tables.values():
        if rows:
            return str(rows[0].get("snapshot_date") or rows[0].get("source_snapshot_date"))
    raise ValueError("Cannot build Silver without a snapshot date")


__all__ = ["SILVER_FIELDS", "SILVER_TABLES", "apply_registry_states", "build_silver"]
