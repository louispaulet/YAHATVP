import json
from pathlib import Path

from hatvp.parser import parse_xml
from hatvp.quality_triage import (
    build_review_register,
    declaration_xml_fingerprints,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _evidence(flagged_records: int) -> dict:
    return {
        "snapshot_date": "2026-08-16",
        "raw_xml_uri": "fixture://declarations.xml",
        "raw_xml_sha256": "fixture-sha",
        "quality_report": {"quality": {"flagged_records": flagged_records}},
    }


def _anomaly(table_name: str, row: dict, reason: str, record_key: object = None) -> dict:
    return {
        "table_name": table_name,
        "declaration_uuid": row.get("declaration_uuid"),
        "record_key": record_key,
        "quality_status": "FLAG",
        "quality_reason": reason,
        "raw_record_json": json.dumps(row, ensure_ascii=False, sort_keys=True),
    }


def test_duplicate_uuid_fingerprints_and_asset_flags_are_source_linked() -> None:
    source_path = FIXTURES / "quality_triage.xml"
    tables = parse_xml(source_path, "2026-08-16")
    fingerprints = declaration_xml_fingerprints(source_path)

    duplicate_rows = [
        row for row in tables["declarations"] if row["declaration_uuid"] == "triage-duplicate"
    ]
    negative_row = next(
        row for row in tables["assets"] if row["declaration_uuid"] == "triage-negative"
    )
    outlier_row = next(
        row for row in tables["assets"] if row["declaration_uuid"] == "triage-outlier"
    )
    anomalies = [
        *[
            _anomaly(
                "declarations",
                row,
                "duplicate declaration_uuid: triage-duplicate",
            )
            for row in duplicate_rows
        ],
        _anomaly("assets", negative_row, "negative asset value"),
        _anomaly(
            "assets",
            outlier_row,
            "robust statistical asset outlier; retained for review",
        ),
    ]

    assert len(fingerprints["triage-duplicate"]) == 2
    assert len({item["canonical_xml_sha256"] for item in fingerprints["triage-duplicate"]}) == 2
    assert len({item["semantic_xml_sha256"] for item in fingerprints["triage-duplicate"]}) == 2

    review = build_review_register(
        anomalies=anomalies,
        source_tables=tables,
        persisted_tables={name: tables[name] for name in ("declarations", "people", "assets")},
        fingerprints=fingerprints,
        evidence=_evidence(len(anomalies)),
    )

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
    tables = parse_xml(FIXTURES / "declarations.xml", "2026-08-16")
    people = tables["people"]
    anomalies = [
        _anomaly(
            "people", row, "repeated name; retained because names are not stable identity keys"
        )
        for row in people
    ]

    review = build_review_register(
        anomalies=anomalies,
        source_tables=tables,
        persisted_tables={"people": people},
        fingerprints=declaration_xml_fingerprints(FIXTURES / "declarations.xml"),
        evidence=_evidence(len(anomalies)),
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
