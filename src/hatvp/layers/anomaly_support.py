"""Shared row identity and evidence helpers for Silver anomaly rules."""

from __future__ import annotations

import json
from typing import Any


def parent_map(tables: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """Index declarations so child rows inherit role, amendment, and dates."""

    return {row.get("bronze_record_key", ""): row for row in tables.get("declarations", [])}


def declarant_key(row: dict[str, Any], parent: dict[str, Any] | None = None) -> str:
    """Prefer stable HATVP UUIDs and expose unresolved identity explicitly."""

    value = row.get("declaration_uuid") or (parent or {}).get("declaration_uuid")
    return str(value) if value else f"review:{row.get('bronze_record_key', 'unknown')}"


def record_ref(table: str, row: dict[str, Any]) -> str:
    """Return the stable Silver row reference used by anomaly evidence."""

    return f"{table}:{row.get('bronze_record_key') or row.get('source_record_id') or id(row)}"


def field_period(row: dict[str, Any], parent: dict[str, Any]) -> str | None:
    """Return the best source period without inventing a normalized field."""

    value = row.get("income_year") or parent.get("date_debut_mandat") or parent.get("date_depot")
    return str(value) if value is not None else None


def occurrence(
    rule: str, row: dict[str, Any], parent: dict[str, Any], field: str, evidence: Any
) -> dict[str, Any]:
    """Build one serializable anomaly occurrence with complete provenance."""

    return {
        "record_ref": record_ref(row.get("_table", "unknown"), row),
        "table_name": row.get("_table", "unknown"),
        "rule_id": rule,
        "severity": "review",
        "declarant_key": declarant_key(row, parent),
        "declaration_id": parent.get("declaration_uuid") or row.get("declaration_uuid"),
        "declaration_version": parent.get("declaration_version") or row.get("declaration_version"),
        "field": field,
        "period": field_period(row, parent),
        "observed_value": row.get(field),
        "evidence": evidence,
        "source_snapshot_date": row.get("source_snapshot_date") or row.get("snapshot_date"),
        "source_format": row.get("source_format"),
        "source_uri_or_object": row.get("source_object") or row.get("source_url"),
        "source_location": row.get("source_location"),
    }


def numeric_value(row: dict[str, Any]) -> float | None:
    """Return numeric values used by compensation and asset rules."""

    value = row.get("normalized_value")
    return float(value) if isinstance(value, (int, float)) and value is not None else None


def role_name(row: dict[str, Any]) -> str:
    """Return the source section or description used as comparison context."""

    return str(row.get("income_type") or row.get("source_section") or "")


def text_value(value: Any) -> str | None:
    """Keep scalar and structured evidence within text-valued table fields."""

    return (
        None
        if value is None
        else value
        if isinstance(value, str)
        else json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    )


__all__ = [
    "declarant_key",
    "field_period",
    "numeric_value",
    "occurrence",
    "parent_map",
    "record_ref",
    "role_name",
    "text_value",
]
