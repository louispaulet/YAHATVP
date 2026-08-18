"""Deterministic anomaly registry upserts and lifecycle transitions."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from typing import Any

from .anomaly_support import text_value


def anomaly_id(anomaly_key: str) -> str:
    """Return the stable evidence identifier for one logical anomaly."""

    return f"anomaly_{hashlib.sha256(anomaly_key.encode()).hexdigest()[:24]}"


def upsert_registry(
    occurrences: list[dict[str, Any]], existing: list[dict[str, Any]], snapshot_date: str
) -> list[dict[str, Any]]:
    """Merge current occurrences without duplicating retry or snapshot alerts."""

    merged = {str(row["anomaly_key"]): dict(row) for row in existing if row.get("anomaly_key")}
    for occurrence in occurrences:
        key = str(occurrence["anomaly_key"])
        previous = merged.get(key, {})
        snapshots = _snapshots(previous.get("seen_snapshots"))
        repeated = snapshot_date in snapshots
        snapshots.add(snapshot_date)
        status = (
            "regression"
            if previous.get("status") == "regression"
            or previous.get("status") in {"superseded", "resolved"}
            and not repeated
            else "known/reported"
            if previous
            else "active"
        )
        merged[key] = _registry_row(occurrence, previous, snapshot_date, snapshots, status)
    return sorted(merged.values(), key=lambda row: str(row["anomaly_key"]))


def _registry_row(
    item: dict[str, Any], previous: dict[str, Any], snapshot: str, snapshots: set[str], status: str
) -> dict[str, Any]:
    now = date.today().isoformat()
    return {
        "anomaly_id": previous.get("anomaly_id") or anomaly_id(item["anomaly_key"]),
        "anomaly_key": item["anomaly_key"],
        "rule_id": item["rule_id"],
        "severity": item.get("severity", "review"),
        "declarant_key": item.get("declarant_key"),
        "field": item.get("field"),
        "period": text_value(item.get("period")),
        "observed_value": text_value(item.get("observed_value")),
        "expected_value_or_range": text_value(item.get("evidence", {}).get("expected"))
        if isinstance(item.get("evidence"), dict)
        else None,
        "evidence": json.dumps(
            {"record_ref": item.get("record_ref"), **(item.get("evidence") or {})},
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        ),
        "record_ref": item.get("record_ref"),
        "first_seen": previous.get("first_seen") or snapshot,
        "last_seen": snapshot,
        "is_latest_declaration": False,
        "superseded_by": previous.get("superseded_by"),
        "previously_reported": bool(previous) or bool(item.get("previously_reported")),
        "status": status,
        "declaration_id": item.get("declaration_id"),
        "declaration_version": item.get("declaration_version"),
        "source_snapshot_date": item.get("source_snapshot_date"),
        "source_format": item.get("source_format"),
        "source_uri_or_object": item.get("source_uri_or_object"),
        "source_location": item.get("source_location"),
        "candidate_value_or_range": text_value(item.get("evidence", {}).get("candidates"))
        if isinstance(item.get("evidence"), dict)
        else None,
        "metric_eligible": False,
        "active_in_gold": False,
        "detected_at": previous.get("detected_at") or now,
        "occurrence_count": len(snapshots),
        "seen_snapshots": json.dumps(sorted(snapshots)),
        "snapshot_date": snapshot,
    }


def _snapshots(value: Any) -> set[str]:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return {str(item) for item in parsed}
        except json.JSONDecodeError:
            return {value}
    return set(value or ())
