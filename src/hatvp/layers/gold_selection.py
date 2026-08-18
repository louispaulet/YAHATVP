"""Deterministic Gold declaration ordering and selection keys."""

from __future__ import annotations

from datetime import date
from typing import Any


def latest_declaration_keys(rows: list[dict[str, Any]]) -> set[str]:
    """Select one declaration occurrence per declarant, role, and period."""

    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = selection_key(row)
        if key not in groups or declaration_order(row) > declaration_order(groups[key]):
            groups[key] = row
    return {
        str(row["bronze_record_key"]) for row in groups.values() if row.get("bronze_record_key")
    }


def selection_key(row: dict[str, Any]) -> tuple[str, str, str]:
    """Scope latest selection to declarant, role/mandate, and period."""

    identity = str(row.get("declarant_key") or row.get("declaration_uuid") or "review:unknown")
    role = str(
        row.get("mandat_label") or row.get("mandat_type") or row.get("declaration_type_id") or ""
    )
    period = str(
        row.get("date_debut_mandat") or row.get("date_depot") or row.get("snapshot_date") or ""
    )
    return identity, role, period


def declaration_order(row: dict[str, Any]) -> tuple[str, int, str, str, str]:
    """Order by source deposit/date evidence, amendment, snapshot, then key."""

    depot = str(row.get("date_depot") or "")
    amended = str(row.get("declaration_modificative", "")).casefold() in {"true", "1", "oui"}
    last = str(
        row.get("date_derniere_declaration") or row.get("date_derniere_declaration_raw") or ""
    )
    return (
        depot,
        int(amended),
        last,
        str(row.get("snapshot_date") or ""),
        str(row.get("bronze_record_key") or ""),
    )


def selection_date(row: dict[str, Any]) -> date | None:
    """Expose the primary date used by operational validation reports."""

    value = row.get("date_depot") or row.get("snapshot_date")
    try:
        return date.fromisoformat(str(value)) if value else None
    except ValueError:
        return None


def selection_fields() -> tuple[str, ...]:
    """Return fields whose source evidence participates in latest ordering."""

    return (
        "date_depot",
        "declaration_modificative",
        "date_derniere_declaration_raw",
        "snapshot_date",
        "bronze_record_key",
    )


__all__ = [
    "declaration_order",
    "latest_declaration_keys",
    "selection_date",
    "selection_fields",
    "selection_key",
]
