"""Quality identity checks retain duplicate rows and flag stable-ID collisions."""

from hatvp.quality import run_quality_checks
from hatvp.quality_helpers import add_anomaly, previous_summary
from hatvp.triage_evidence_helpers import normal_name
from tests.quality_support import tables


def test_duplicate_names_are_flagged_but_not_deduplicated() -> None:
    value = tables()

    result = run_quality_checks(value, snapshot_date="2026-08-16")

    assert len(value["people"]) == 2
    assert result.report["checks"]["duplicate_person_names"] == 1
    assert result.report["checks"]["huge_income"] == 1
    assert result.report["quality"]["flagged_records"] >= 3
    assert all(row["quality_status"] == "FLAG" for row in value["people"])


def test_duplicate_stable_identifier_is_reported() -> None:
    value = tables()
    value["declarations"].append({"declaration_uuid": "a"})

    result = run_quality_checks(value, snapshot_date="2026-08-16")

    assert result.report["checks"]["duplicate_declaration_ids"] == 1
    assert result.report["quality"]["warnings"] > 0


def test_identity_helpers_normalize_names_and_previous_reports() -> None:
    assert normal_name("  Alice   Dupont ") == "alice dupont"
    assert (
        previous_summary({"status": "warning", "quality": {"flagged_records": 2}})[
            "flagged_records"
        ]
        == 2
    )
    assert previous_summary(None) == {}


def test_add_anomaly_records_the_raw_row_without_mutating_it() -> None:
    row = {"declaration_uuid": "a", "raw_value": "-1"}
    anomalies: list[dict] = []

    add_anomaly(anomalies, table_name="assets", row=row, reason="negative asset value")

    assert row["declaration_uuid"] == "a"
    assert row["raw_value"] == "-1"
    assert row["quality_status"] == "FLAG"
    assert anomalies[0]["table_name"] == "assets"
    assert anomalies[0]["quality_status"] == "FLAG"


def test_identity_quality_report_counts_all_normalized_tables() -> None:
    value = tables()

    result = run_quality_checks(value, snapshot_date="2026-08-16")

    assert result.report["counts"]["declarations"] == 2
    assert result.report["counts"]["people"] == 2
    assert result.report["counts"]["liste"] == 0
    assert set(result.report["counts"]) == set(value)


def test_duplicate_people_keep_distinct_declaration_identifiers() -> None:
    value = tables()

    run_quality_checks(value, snapshot_date="2026-08-16")

    assert {row["declaration_uuid"] for row in value["people"]} == {"a", "b"}
    assert all(
        row["quality_reason"]
        == "repeated name; retained because names are not stable identity keys"
        for row in value["people"]
    )
