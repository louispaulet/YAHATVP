"""Source-format and geography consistency rules for HATVP evidence."""

from __future__ import annotations

from typing import Any

from .anomaly_support import occurrence
from .rules import conflicting_sources


def source_anomalies(
    rows: list[dict[str, Any]], parents: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Flag explicit cross-format conflicts and department/municipality mismatches."""

    results: list[dict[str, Any]] = []
    for row in rows:
        parent = parents.get(row.get("bronze_record_key", ""), {})
        values = conflicting_sources(row)
        if values:
            results.append(
                occurrence("SOURCE_CROSS_FORMAT", row, parent, "raw_value", {"values": values})
            )
        if geo_mismatch(row):
            results.append(
                occurrence(
                    "GEO_DEPARTMENT_MUNICIPALITY",
                    row,
                    parent,
                    "department",
                    {"municipality_department": row["municipality_department"]},
                )
            )
    return results


def geo_mismatch(row: dict[str, Any]) -> bool:
    """Return whether explicit source department observations disagree."""

    return bool(
        row.get("department")
        and row.get("municipality_department")
        and row["department"] != row["municipality_department"]
    )


def source_locations(row: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return source URI and field location for review evidence."""

    return row.get("source_object") or row.get("source_url"), row.get("source_location")


def source_rule_ids() -> tuple[str, ...]:
    """Expose source consistency rule IDs for documentation/tests."""

    return ("GEO_DEPARTMENT_MUNICIPALITY", "SOURCE_CROSS_FORMAT")


def source_value_count(row: dict[str, Any]) -> int:
    """Count explicitly supplied cross-format values without inferring precedence."""

    values = row.get("cross_format_values") or row.get("source_values")
    return len(values) if isinstance(values, dict) else 0


__all__ = [
    "geo_mismatch",
    "source_anomalies",
    "source_locations",
    "source_rule_ids",
    "source_value_count",
]
