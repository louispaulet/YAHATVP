"""Warning-streak and flagged-record regression telemetry."""

from __future__ import annotations

from typing import Any

from .quality_helpers import previous_summary

REGRESSION_THRESHOLD = 0.10


def telemetry(
    status: str, anomalies: list[dict[str, Any]], previous_report: dict[str, Any] | None
) -> dict[str, Any]:
    previous = previous_summary(previous_report)
    old_flagged = previous.get("flagged_records")
    old_flagged = old_flagged if isinstance(old_flagged, int) and old_flagged >= 0 else None
    old_streak = previous.get("warning_streak", 0)
    old_streak = old_streak if isinstance(old_streak, int) and old_streak >= 0 else 0
    streak = (
        old_streak + 1
        if status == "warning" and previous_report and previous_report.get("status") == "warning"
        else 1
        if status == "warning"
        else 0
    )
    flagged = len(anomalies)
    ratio = None
    regression = False
    if old_flagged is not None:
        if old_flagged == 0:
            regression = flagged > 0
        else:
            ratio = round((flagged - old_flagged) / old_flagged, 6)
            regression = ratio > REGRESSION_THRESHOLD
    return {
        "flagged_records": flagged,
        "previous_flagged_records": old_flagged,
        "flagged_records_increase_ratio": ratio,
        "quality_regression": regression and status in {"ok", "warning"},
        "warning_streak": streak,
    }
