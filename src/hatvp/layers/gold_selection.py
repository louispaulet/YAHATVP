"""Deterministic Gold declaration ordering and selection keys."""

from __future__ import annotations

from datetime import date
from typing import Any

from .publication import publication_key


def latest_declaration_keys(rows: list[dict[str, Any]]) -> set[str]:
    """Keep unpublished versions unless a current online version supersedes them."""

    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    versions: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = publication_key(row)
        if key not in versions or _source_order(row) > _source_order(versions[key]):
            versions[key] = row
    for row in versions.values():
        groups.setdefault(selection_key(row), []).append(row)
    selected = set()
    for candidates in groups.values():
        online = [row for row in candidates if row.get("publication_status") != "unpublished"]
        if online:
            latest = max(online, key=declaration_order)
            if latest.get("bronze_record_key"):
                selected.add(str(latest["bronze_record_key"]))
        else:
            selected.update(
                str(row["bronze_record_key"]) for row in candidates if row.get("bronze_record_key")
            )
    return selected


def _source_order(row: dict[str, Any]) -> tuple[int, str]:
    """Prefer official observations when one version is present in several sources."""

    return int(row.get("ingestion_source") == "hatvp_website"), str(row.get("snapshot_date") or "")


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
