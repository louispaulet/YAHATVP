"""Same-period compensation conflict and amendment supersession rules."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .anomaly_support import declarant_key, occurrence


def conflict_anomalies(
    rows: list[dict[str, Any]], parents: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Flag differing compensation values for one person, role, and period."""

    groups: defaultdict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        parent = parents.get(row.get("bronze_record_key", ""), {})
        period = str(row.get("income_year") or "")
        role = str(row.get("income_type") or row.get("source_section") or "")
        if period and row.get("normalized_value") is not None:
            groups[(declarant_key(row, parent), role, period)].append(row)
    return [
        item
        for values in groups.values()
        if len({row.get("normalized_value") for row in values}) > 1
        for item in _conflict_group(values, parents)
    ]


def _conflict_group(
    rows: list[dict[str, Any]], parents: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    ordered = sorted(
        rows, key=lambda row: str(row.get("snapshot_date") or row.get("bronze_record_key") or "")
    )
    latest = ordered[-1]
    values = [row.get("normalized_value") for row in rows]
    results: list[dict[str, Any]] = []
    for row in ordered:
        parent = parents.get(row.get("bronze_record_key", ""), {})
        results.append(
            occurrence(
                "COMP_CONFLICT_SAME_PERIOD", row, parent, "normalized_value", {"values": values}
            )
        )
        if row is not latest:
            results.append(
                occurrence(
                    "COMP_SUPERSEDED_DECLARATION",
                    row,
                    parent,
                    "normalized_value",
                    {"superseded_by": latest.get("bronze_record_key")},
                )
            )
    return results


def conflict_rule_ids() -> tuple[str, ...]:
    """Expose both conflict lifecycle rule IDs for acceptance coverage."""

    return ("COMP_CONFLICT_SAME_PERIOD", "COMP_SUPERSEDED_DECLARATION")


def conflict_period(row: dict[str, Any]) -> str | None:
    """Return the period used for same-year comparison."""

    value = row.get("income_year")
    return str(value) if value is not None else None


__all__ = ["conflict_anomalies", "conflict_period", "conflict_rule_ids"]
