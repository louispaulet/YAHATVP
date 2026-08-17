"""Quality-check façade preserving the report contract used by the pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .quality_checks import structural_checks
from .quality_numeric import numeric_checks
from .quality_telemetry import REGRESSION_THRESHOLD, telemetry

logger = logging.getLogger(__name__)


@dataclass
class QualityResult:
    report: dict[str, Any]
    anomalies: list[dict[str, Any]]

    @property
    def has_errors(self) -> bool:
        return self.report["quality"]["errors"] > 0

    @property
    def has_warnings(self) -> bool:
        return self.report["quality"]["warnings"] > 0 or bool(self.anomalies)


def run_quality_checks(
    tables: dict[str, list[dict[str, Any]]],
    *,
    previous_report: dict[str, Any] | None = None,
    snapshot_date: str,
) -> QualityResult:
    anomalies: list[dict[str, Any]] = []
    errors, warnings, checks, null_rates = structural_checks(tables, previous_report, anomalies)
    numeric_warnings, numeric = numeric_checks(tables, anomalies)
    checks.update(numeric)
    warnings += numeric_warnings
    status = "error" if errors else "warning" if warnings else "ok"
    quality = telemetry(status, anomalies, previous_report)
    report = {
        "snapshot_date": snapshot_date,
        "status": status,
        "counts": {name: len(rows) for name, rows in tables.items()},
        "null_rates": null_rates,
        "quality": {"errors": errors, "warnings": warnings, **quality},
        "checks": checks,
    }
    _log_quality(snapshot_date, status, report)
    return QualityResult(report=report, anomalies=anomalies)


def _log_quality(snapshot_date: str, status: str, report: dict[str, Any]) -> None:
    quality = report["quality"]
    logger.info(
        "quality_complete",
        extra={
            "event": "quality_complete",
            "status": status,
            "counts": report["counts"],
            "errors": quality["errors"],
            "warnings": quality["warnings"],
            "flagged_records": quality["flagged_records"],
            "previous_flagged_records": quality["previous_flagged_records"],
            "flagged_records_increase_ratio": quality["flagged_records_increase_ratio"],
            "quality_regression": quality["quality_regression"],
            "warning_streak": quality["warning_streak"],
        },
    )
    if quality["warning_streak"] >= 2:
        logger.warning(
            "quality_warning_streak",
            extra={
                "event": "quality_warning_streak",
                "status": status,
                "snapshot_date": snapshot_date,
                "warning_streak": quality["warning_streak"],
                "flagged_records": quality["flagged_records"],
            },
        )
    if quality["quality_regression"]:
        logger.warning(
            "quality_regression",
            extra={
                "event": "quality_regression",
                "status": status,
                "snapshot_date": snapshot_date,
                "metric": "flagged_records",
                "previous_flagged_records": quality["previous_flagged_records"],
                "flagged_records": quality["flagged_records"],
                "relative_increase": quality["flagged_records_increase_ratio"],
                "threshold": REGRESSION_THRESHOLD,
            },
        )


__all__ = ["QualityResult", "run_quality_checks"]
