"""Choose one latest declaration occurrence before anomaly detection."""

from __future__ import annotations

from typing import Any

from .gold_selection import declaration_order
from .silver_dedupe import unique_rows

TABLES = ("declarations", "people", "incomes", "assets")
QUALITY_IDENTITY_FIELD = "declaration_uuid"


def dedupe_for_quality(
    current: dict[str, list[dict[str, Any]]], history: dict[str, list[dict[str, Any]]]
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    """Retain Bronze rows but give anomaly rules one latest row per UUID."""

    combined = {
        name: unique_rows([*history.get(name, []), *current.get(name, [])]) for name in TABLES
    }
    selected = _selected_declaration_keys(combined["declarations"])
    return _filter(current, selected), _filter(history, selected)


def _selected_declaration_keys(rows: list[dict[str, Any]]) -> set[str]:
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        identity = str(row.get(QUALITY_IDENTITY_FIELD) or row.get("bronze_record_key") or "")
        if not identity:
            continue
        if identity not in latest or _quality_order(row) > _quality_order(latest[identity]):
            latest[identity] = row
    return {str(row.get("bronze_record_key")) for row in latest.values()}


def _quality_order(row: dict[str, Any]) -> tuple[Any, ...]:
    source_priority = 1 if row.get("ingestion_source") == "hatvp_website" else 0
    return (*declaration_order(row), source_priority)


def _filter(
    tables: dict[str, list[dict[str, Any]]], selected: set[str]
) -> dict[str, list[dict[str, Any]]]:
    return {
        name: [
            row
            for row in tables.get(name, [])
            if str(row.get("bronze_record_key") or "") in selected
        ]
        for name in TABLES
    }


def quality_declaration_count(
    current: dict[str, list[dict[str, Any]]], history: dict[str, list[dict[str, Any]]]
) -> int:
    """Return the number of declaration rows anomaly rules are allowed to inspect."""

    filtered, _ = dedupe_for_quality(current, history)
    return len(filtered["declarations"])


def quality_identity_field() -> str:
    """Expose the stable field that controls pre-anomaly declaration selection."""

    return QUALITY_IDENTITY_FIELD


def quality_table_names() -> tuple[str, ...]:
    """Expose the child tables filtered with the selected declaration keys."""

    return TABLES


__all__ = [
    "dedupe_for_quality",
    "quality_declaration_count",
    "quality_identity_field",
    "quality_table_names",
]
