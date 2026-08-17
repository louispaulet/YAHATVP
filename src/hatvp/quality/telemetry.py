"""Warning-streak and flagged-record regression telemetry."""

from __future__ import annotations

from typing import Any

from .helpers import previous_summary

REGRESSION_THRESHOLD = 0.10


def warning_streak(status: str, previous_report: dict[str, Any] | None) -> int:
    """Advance warning streaks only across consecutive warning reports."""

    previous = previous_summary(previous_report)
    old = previous.get("warning_streak", 0)
    old = old if isinstance(old, int) and old >= 0 else 0
    continues = previous_report and previous_report.get("status") == "warning"
    return old + 1 if status == "warning" and continues else 1 if status == "warning" else 0


def flagged_ratio(flagged: int, previous: int | None) -> float | None:
    """Return a rounded relative increase, with zero handled as a new finding."""

    if previous is None or previous == 0:
        return None
    return round((flagged - previous) / previous, 6)


def is_regression(flagged: int, previous: int | None) -> bool:
    """Apply the configured increase threshold, including zero-to-positive changes."""

    if previous == 0:
        return flagged > 0
    ratio = flagged_ratio(flagged, previous)
    return ratio is not None and ratio > REGRESSION_THRESHOLD


def telemetry(
    status: str, anomalies: list[dict[str, Any]], previous_report: dict[str, Any] | None
) -> dict[str, Any]:
    previous = previous_summary(previous_report)
    old_flagged = previous.get("flagged_records")
    old_flagged = old_flagged if isinstance(old_flagged, int) and old_flagged >= 0 else None
    streak = warning_streak(status, previous_report)
    flagged = len(anomalies)
    ratio = None
    regression = False
    if old_flagged is not None:
        if old_flagged == 0:
            regression = flagged > 0
        else:
            ratio = flagged_ratio(flagged, old_flagged)
            regression = is_regression(flagged, old_flagged)
    return {
        "flagged_records": flagged,
        "previous_flagged_records": old_flagged,
        "flagged_records_increase_ratio": ratio,
        "quality_regression": regression and status in {"ok", "warning"},
        "warning_streak": streak,
    }


__all__ = [
    "REGRESSION_THRESHOLD",
    "flagged_ratio",
    "is_regression",
    "telemetry",
    "warning_streak",
]
