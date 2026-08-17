"""Fixture helpers for source-linked quality review tests."""

from __future__ import annotations

import json
from pathlib import Path

from hatvp.parser import parse_xml

FIXTURES = Path(__file__).parent / "fixtures"


def evidence(flagged_records: int) -> dict:
    """Build the evidence envelope expected by the review register."""

    return {
        "snapshot_date": "2026-08-16",
        "raw_xml_uri": "fixture://declarations.xml",
        "raw_xml_sha256": "fixture-sha",
        "quality_report": {"quality": {"flagged_records": flagged_records}},
    }


def anomaly(table_name: str, row: dict, reason: str, record_key: object = None) -> dict:
    """Serialize one flagged normalized row exactly as the quality stage does."""

    return {
        "table_name": table_name,
        "declaration_uuid": row.get("declaration_uuid"),
        "record_key": record_key,
        "quality_status": "FLAG",
        "quality_reason": reason,
        "raw_record_json": json.dumps(row, ensure_ascii=False, sort_keys=True),
    }


def fixture_tables(name: str = "declarations.xml") -> dict[str, list[dict]]:
    """Parse a named XML fixture with the production parser boundary."""

    return parse_xml(FIXTURES / name, "2026-08-16")


def persisted_subset(tables: dict[str, list[dict]], *names: str) -> dict[str, list[dict]]:
    """Select only the tables persisted by the curated review evidence stage."""

    return {name: tables[name] for name in names}


def flagged_asset_rows(tables: dict[str, list[dict]]) -> tuple[dict, dict]:
    """Return the negative and statistical-outlier asset rows from the fixture."""

    negative = next(row for row in tables["assets"] if row["declaration_uuid"] == "triage-negative")
    outlier = next(row for row in tables["assets"] if row["declaration_uuid"] == "triage-outlier")
    return negative, outlier


def duplicate_declarations(tables: dict[str, list[dict]], uuid: str) -> list[dict]:
    """Return every repeated source declaration occurrence for one UUID."""

    return [row for row in tables["declarations"] if row.get("declaration_uuid") == uuid]


def review_record_count(review: dict) -> int:
    """Read the register count through its stable machine-readable summary."""

    return int(review["summary"]["flagged_records"])


def review_is_reconciled(review: dict) -> bool:
    """Read the register reconciliation result for focused assertions."""

    return bool(review["summary"]["reconciliation_passed"])
