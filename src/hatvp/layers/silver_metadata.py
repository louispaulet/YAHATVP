"""Field-level anomaly metadata attached to Silver and Gold rows."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from .anomaly_support import record_ref
from .dob_quality import quality_fields


def occurrences_by_ref(
    items: list[dict[str, Any]], registry: dict[str, dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    """Group rule occurrences by stable source row and attach registry IDs."""

    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        enriched = dict(item)
        registered = registry.get(item["anomaly_key"])
        enriched["anomaly_id"] = registered.get("anomaly_id") if registered else None
        enriched["status"] = registered.get("status", "active") if registered else "active"
        grouped[item["record_ref"]].append(enriched)
    return grouped


def annotate_row(
    table: str,
    row: dict[str, Any],
    parents: dict[str, dict[str, Any]],
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Copy a Bronze row and add anomaly, provenance, and eligibility metadata."""

    parent = parents.get(row.get("bronze_record_key", ""), {})
    rules = sorted({item["rule_id"] for item in items})
    active = bool(items) and not all(
        item.get("status") in {"superseded", "resolved"} for item in items
    )
    regression = any(item.get("status") == "regression" for item in items)
    status = "clean" if not items else ("regression" if regression else "active")
    eligibility = field_eligibility(table, items)
    metadata = {
        **row,
        "declarant_key": row.get("declaration_uuid")
        or parent.get("declaration_uuid")
        or f"review:{row.get('bronze_record_key', 'unknown')}",
        "anomaly_status": status,
        "anomaly_rule_ids": json.dumps(rules, separators=(",", ":")),
        "anomaly_registry_ids": json.dumps(
            sorted({item["anomaly_id"] for item in items if item.get("anomaly_id")}),
            separators=(",", ":"),
        ),
        "anomaly_evidence_json": json.dumps(items, ensure_ascii=False, sort_keys=True, default=str),
        "field_metric_eligibility_json": json.dumps(eligibility, sort_keys=True),
        "metric_eligible": all(eligibility.values()) if eligibility else True,
        "anomaly_active": active,
        "previously_reported": any(item.get("previously_reported") for item in items),
        "is_latest_declaration": False,
        "active_in_gold": False,
        "superseded_by": next(
            (
                item.get("evidence", {}).get("superseded_by")
                for item in items
                if item.get("evidence", {}).get("superseded_by")
            ),
            None,
        ),
    }
    if table == "people":
        metadata.update(quality_fields(row, items))
    return metadata


def field_eligibility(table: str, items: list[dict[str, Any]]) -> dict[str, bool]:
    """Make only affected fields ineligible while retaining the source row."""

    fields = {item["field"] for item in items}
    if table in {"incomes", "assets"}:
        return {"normalized_value": "normalized_value" not in fields}
    if table == "people":
        return {"date_naissance": "date_naissance" not in fields}
    return {"declaration": not bool(items)}


def annotate_tables(
    tables: dict[str, list[dict[str, Any]]],
    parents: dict[str, dict[str, Any]],
    grouped: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    """Annotate a mapping without changing source row ordering."""

    return {
        name: [
            annotate_row(name, row, parents, grouped.get(record_ref(name, row), [])) for row in rows
        ]
        for name, rows in tables.items()
    }


__all__ = ["annotate_row", "annotate_tables", "field_eligibility", "occurrences_by_ref"]
