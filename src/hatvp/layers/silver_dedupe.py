"""Retry-safe Silver row identity without collapsing repeated source occurrences."""

from __future__ import annotations

from typing import Any

DETAIL_FIELDS = (
    "source_location",
    "source_section",
    "source_item_index",
    "income_category_index",
    "remuneration_index",
    "income_year",
    "raw_value",
)


def unique_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse exact retry copies while retaining repeated UUID occurrences."""

    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        unique[row_identity(row)] = row
    return list(unique.values())


def row_identity(row: dict[str, Any]) -> tuple[str, str, str]:
    """Return the stable Silver identity for one normalized source row."""

    return (
        source_record_key(row),
        snapshot_key(row),
        detail_key(row),
    )


def source_record_key(row: dict[str, Any]) -> str:
    """Prefer the version-aware Bronze key and retain legacy compatibility."""

    return str(row.get("bronze_record_key") or row.get("source_record_id") or "")


def snapshot_key(row: dict[str, Any]) -> str:
    """Keep retry deduplication scoped to one immutable source snapshot."""

    return str(row.get("snapshot_date") or row.get("source_snapshot_date") or "")


def detail_key(row: dict[str, Any]) -> str:
    """Distinguish child rows that share a declaration UUID and snapshot."""

    return "|".join(str(row.get(field) or "") for field in DETAIL_FIELDS)


def is_retry_copy(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """Report whether two rows would occupy the same Silver identity."""

    return row_identity(left) == row_identity(right)


def preserve_repeated_occurrences(rows: list[dict[str, Any]]) -> bool:
    """Document the invariant that distinct detail rows survive deduplication."""

    return len(unique_rows(rows)) == len({row_identity(row) for row in rows})


__all__ = [
    "DETAIL_FIELDS",
    "detail_key",
    "is_retry_copy",
    "preserve_repeated_occurrences",
    "row_identity",
    "snapshot_key",
    "source_record_key",
    "unique_rows",
]
