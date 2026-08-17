"""Reusable anomaly, duplicate, outlier, and previous-report helpers."""

from __future__ import annotations

import json
from collections import Counter
from statistics import median
from typing import Any


def add_anomaly(
    anomalies: list[dict[str, Any]],
    *,
    table_name: str,
    row: dict[str, Any],
    reason: str,
    status: str = "FLAG",
) -> None:
    row["quality_status"] = status
    row["quality_reason"] = reason
    anomalies.append(
        {
            "table_name": table_name,
            "declaration_uuid": row.get("declaration_uuid"),
            "record_key": row.get("raw_record_json") or row.get("source_item_index"),
            "quality_status": status,
            "quality_reason": reason,
            "raw_record_json": json.dumps(row, ensure_ascii=False, sort_keys=True, default=str),
        }
    )


def duplicate_count(rows: list[dict[str, Any]], key: str) -> int:
    values = [row.get(key) for row in rows if row.get(key)]
    return sum(count - 1 for count in Counter(values).values() if count > 1)


def previous_summary(previous_report: dict[str, Any] | None) -> dict[str, Any]:
    if not previous_report or previous_report.get("status") not in {"ok", "warning"}:
        return {}
    quality = previous_report.get("quality")
    return quality if isinstance(quality, dict) else {}


def catastrophic_reduction(current: int, previous: int | None) -> bool:
    return previous is not None and previous >= 20 and current < previous * 0.5


def robust_outliers(
    rows: list[dict[str, Any]],
    *,
    table_name: str,
    field_name: str,
    reason: str,
    anomalies: list[dict[str, Any]],
) -> int:
    values = [row.get(field_name) for row in rows if isinstance(row.get(field_name), (int, float))]
    if len(values) < 8:
        return 0
    center = median(values)
    mad = median([abs(value - center) for value in values])
    if mad == 0:
        return 0
    scale = 1.4826 * mad
    flagged = 0
    for row in rows:
        value = row.get(field_name)
        if (
            isinstance(value, (int, float))
            and row.get("quality_status") != "FLAG"
            and abs(value - center) / scale > 10
        ):
            add_anomaly(anomalies, table_name=table_name, row=row, reason=reason)
            flagged += 1
    return flagged
