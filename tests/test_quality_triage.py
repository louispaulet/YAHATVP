"""Source-linked quality register acceptance tests."""

from hatvp.triage import build_review_register, declaration_xml_fingerprints
from tests.triage_support import (
    FIXTURES,
    anomaly,
    evidence,
    fixture_tables,
    flagged_asset_rows,
    persisted_subset,
)


def test_duplicate_uuid_fingerprints_and_asset_flags_are_source_linked() -> None:
    tables = fixture_tables("quality_triage.xml")
    fingerprints = declaration_xml_fingerprints(FIXTURES / "quality_triage.xml")
    duplicate_rows = [
        row for row in tables["declarations"] if row["declaration_uuid"] == "triage-duplicate"
    ]
    negative_row, outlier_row = flagged_asset_rows(tables)
    anomalies = [
        *[
            anomaly("declarations", row, "duplicate declaration_uuid: triage-duplicate")
            for row in duplicate_rows
        ],
        anomaly("assets", negative_row, "negative asset value"),
        anomaly("assets", outlier_row, "robust statistical asset outlier; retained for review"),
    ]

    review = build_review_register(
        anomalies=anomalies,
        source_tables=tables,
        persisted_tables=persisted_subset(tables, "declarations", "people", "assets"),
        fingerprints=fingerprints,
        evidence=evidence(len(anomalies)),
    )

    assert len(fingerprints["triage-duplicate"]) == 2
    assert len({item["canonical_xml_sha256"] for item in fingerprints["triage-duplicate"]}) == 2
    assert review["summary"]["flagged_records"] == 4
    assert review["summary"]["reconciliation_passed"] is True
    assert review["summary"]["source_match_counts"] == {"matched": 4}
    assert review["summary"]["disposition_counts"] == {
        "duplicate_source_identifier": 2,
        "source_consistent_outlier": 1,
        "source_valid_flag": 1,
    }
    assert review["duplicate_uuid_groups"][0]["content_classification"] == "conflicting"
    assert all(row["source_evidence"]["source_match"] for row in review["records"])


def test_duplicate_uuid_whitespace_is_semantically_identical() -> None:
    fingerprints = declaration_xml_fingerprints(FIXTURES / "quality_triage.xml")
    occurrences = fingerprints["triage-whitespace"]

    assert len({item["canonical_xml_sha256"] for item in occurrences}) == 2
    assert len({item["semantic_xml_sha256"] for item in occurrences}) == 1


def test_repeated_names_are_grouped_without_deduplication() -> None:
    tables = fixture_tables()
    people = tables["people"]
    anomalies = [
        anomaly("people", row, "repeated name; retained because names are not stable identity keys")
        for row in people
    ]

    review = build_review_register(
        anomalies=anomalies,
        source_tables=tables,
        persisted_tables={"people": people},
        fingerprints=declaration_xml_fingerprints(FIXTURES / "declarations.xml"),
        evidence=evidence(len(anomalies)),
    )

    assert review["summary"]["flagged_records"] == 2
    assert review["summary"]["disposition_counts"] == {"expected_identity_collision": 2}
    assert {row["declaration_uuid"] for row in review["records"]} == {
        "fixture-uuid-1",
        "fixture-uuid-2",
    }
    assert all(
        row["source_evidence"]["distinct_declaration_uuid_count"] == 2 for row in review["records"]
    )
