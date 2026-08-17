"""Quality history, warning streak, regression, and reduction telemetry tests."""

import logging

from hatvp.quality import run_quality_checks
from hatvp.quality.telemetry import flagged_ratio, is_regression, warning_streak
from tests.quality_support import clean_tables, tables


def test_catastrophic_row_count_reduction_is_explicitly_reported() -> None:
    result = run_quality_checks(
        tables(),
        previous_report={"status": "warning", "counts": {"declarations": 100, "people": 100}},
        snapshot_date="2026-08-16",
    )

    assert result.report["checks"]["catastrophic_row_count_reductions"] == 2
    assert result.report["checks"]["catastrophic_row_count_reduction_declarations"] == 1
    assert result.report["checks"]["catastrophic_row_count_reduction_people"] == 1

    failed = run_quality_checks(
        tables(),
        previous_report={"status": "error", "counts": {"declarations": 100, "people": 100}},
        snapshot_date="2026-08-16",
    )
    assert failed.report["checks"]["catastrophic_row_count_reductions"] == 0


def test_quality_warning_streak_emits_only_after_repeated_warnings(caplog) -> None:
    caplog.set_level(logging.WARNING, logger="hatvp")

    result = run_quality_checks(
        tables(),
        previous_report={
            "status": "warning",
            "quality": {"flagged_records": 100, "warning_streak": 1},
        },
        snapshot_date="2026-08-16",
    )

    assert result.report["quality"]["warning_streak"] == 2
    assert any(
        record.__dict__.get("event") == "quality_warning_streak" for record in caplog.records
    )

    caplog.clear()
    clean = run_quality_checks(
        clean_tables(),
        previous_report={
            "status": "warning",
            "quality": {"flagged_records": 100, "warning_streak": 2},
        },
        snapshot_date="2026-08-17",
    )
    assert clean.report["status"] == "ok"
    assert clean.report["quality"]["warning_streak"] == 0
    assert not any(
        record.__dict__.get("event") == "quality_warning_streak" for record in caplog.records
    )


def test_flagged_record_regression_uses_previous_successful_report(caplog) -> None:
    caplog.set_level(logging.WARNING, logger="hatvp")
    below = run_quality_checks(
        tables(),
        previous_report={
            "status": "warning",
            "quality": {"flagged_records": 100, "warning_streak": 1},
        },
        snapshot_date="2026-08-16",
    )
    assert below.report["quality"]["quality_regression"] is False
    caplog.clear()
    above = run_quality_checks(
        tables(),
        previous_report={
            "status": "warning",
            "quality": {"flagged_records": 2, "warning_streak": 1},
        },
        snapshot_date="2026-08-16",
    )
    assert above.report["quality"]["quality_regression"] is True
    assert above.report["quality"]["flagged_records_increase_ratio"] == 0.5
    assert any(record.__dict__.get("event") == "quality_regression" for record in caplog.records)


def test_telemetry_helpers_handle_zero_and_missing_history() -> None:
    assert warning_streak("warning", None) == 1
    assert warning_streak("ok", {"status": "warning"}) == 0
    assert flagged_ratio(3, 2) == 0.5
    assert flagged_ratio(3, 0) is None
    assert is_regression(1, 0)
