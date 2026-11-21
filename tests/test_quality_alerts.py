"""Quality alert fingerprints distinguish persistent evidence from new issues."""

import json

from hatvp.quality.telemetry import telemetry, warning_findings_fingerprint

CHECKS = {"negative_income": 1}


def _anomaly(snapshot: str, value: float) -> dict:
    row = {
        "snapshot_date": snapshot,
        "source_snapshot_date": snapshot,
        "source_observed_at": snapshot,
        "source_object": f"raw/{snapshot}/declarations.xml",
        "source_sha256": snapshot,
        "bronze_record_key": f"bronze-{snapshot}",
        "source_record_id": snapshot,
        "source_item_index": 1,
        "source_location": f"declarations.xml#/declaration[{snapshot}]",
        "declaration_uuid": "fixture-declaration",
        "normalized_value": value,
        "raw_value": str(value),
        "quality_status": "FLAG",
        "quality_reason": "negative income value",
    }
    return {
        "table_name": "incomes",
        "quality_reason": "negative income value",
        "raw_record_json": json.dumps(row),
    }


def test_fingerprint_ignores_snapshot_provenance_but_tracks_source_value() -> None:
    """A repeated source warning keeps its identity across snapshots."""

    first = warning_findings_fingerprint(CHECKS, [_anomaly("2026-11-02", -100)])
    same = warning_findings_fingerprint(CHECKS, [_anomaly("2026-11-16", -100)])
    changed = warning_findings_fingerprint(CHECKS, [_anomaly("2026-11-16", -200)])

    assert first == same
    assert changed != same


def test_repeated_alert_waits_for_changed_evidence_after_initial_streak() -> None:
    """Keep the first two-snapshot alert and alert again for new findings."""

    finding = _anomaly("2026-11-02", -100)
    fingerprint = warning_findings_fingerprint(CHECKS, [finding])
    first_warning = telemetry("warning", [finding], None, CHECKS)
    assert first_warning["warning_streak"] == 1
    assert not first_warning["warning_alert"]

    prior = {
        "status": "warning",
        "quality": {"warning_streak": 1, "warning_findings_fingerprint": fingerprint},
    }
    repeated = telemetry("warning", [finding], prior, CHECKS, "2026-11-02")
    assert repeated["warning_streak"] == 2
    assert repeated["warning_alert"]

    prior["quality"]["warning_streak"] = 2
    unchanged = telemetry("warning", [finding], prior, CHECKS)
    assert unchanged["warning_streak"] == 3
    assert not unchanged["warning_alert"]

    new_finding = _anomaly("2026-11-16", -200)
    changed = telemetry("warning", [new_finding], prior, CHECKS)
    assert changed["warning_alert"]


def test_same_snapshot_retry_does_not_advance_warning_streak() -> None:
    """A retry of an already processed date is not another warning snapshot."""

    finding = _anomaly("2026-11-16", -100)
    fingerprint = warning_findings_fingerprint(CHECKS, [finding])
    prior = {
        "snapshot_date": "2026-11-16",
        "status": "warning",
        "quality": {"warning_streak": 26, "warning_findings_fingerprint": fingerprint},
    }

    retried = telemetry("warning", [finding], prior, CHECKS, "2026-11-16")

    assert retried["warning_streak"] == 26
    assert not retried["warning_alert"]


def test_fingerprint_tracks_warning_checks_without_quarantined_rows() -> None:
    """Warnings represented only by aggregate checks still re-alert on change."""

    one_empty_section = warning_findings_fingerprint({"income_sections_without_rows": 1}, [])
    two_empty_sections = warning_findings_fingerprint({"income_sections_without_rows": 2}, [])

    assert one_empty_section != two_empty_sections
