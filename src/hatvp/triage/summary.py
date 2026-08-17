"""Summary builders for source-linked quality review registers."""

from __future__ import annotations

from collections import Counter
from typing import Any

TRIAGE_SCHEMA_VERSION = "1.0"


def duplicate_groups(fingerprints: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Describe repeated declaration identifiers without dropping occurrences."""

    return [
        {
            "declaration_uuid": uuid,
            "occurrence_count": len(rows),
            "content_classification": _content_classification(rows),
            "canonical_xml_sha256": [row["canonical_xml_sha256"] for row in rows],
            "semantic_xml_sha256": [row["semantic_xml_sha256"] for row in rows],
            "date_depot_raw": [row["date_depot_raw"] for row in rows],
        }
        for uuid, rows in sorted(fingerprints.items())
        if len(rows) > 1
    ]


def _content_classification(rows: list[dict[str, Any]]) -> str:
    """Classify duplicate XML occurrences by semantic hash."""

    hashes = {row["semantic_xml_sha256"] for row in rows}
    return "identical" if len(hashes) == 1 else "conflicting"


def summary_counts(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Return deterministic reason and disposition counters for reporting."""

    return {
        "reason_counts": dict(sorted(Counter(row["quality_reason"] for row in records).items())),
        "disposition_counts": dict(sorted(Counter(row["disposition"] for row in records).items())),
    }


def review_payload(
    records: list[dict[str, Any]], groups: list[dict[str, Any]], evidence: dict[str, Any]
) -> dict[str, Any]:
    """Build the stable machine-readable register envelope and counters."""

    counts = summary_counts(records)
    matches = Counter(
        "matched" if row["source_evidence"]["source_match"] else "unmatched" for row in records
    )
    quality = evidence["quality_report"]["quality"]
    return {
        "schema_version": TRIAGE_SCHEMA_VERSION,
        "snapshot_date": evidence["snapshot_date"],
        "evidence": evidence,
        "quality_report": evidence["quality_report"],
        "summary": {
            "flagged_records": len(records),
            **counts,
            "source_match_counts": dict(sorted(matches.items())),
            "duplicate_uuid_groups": len(groups),
            "unresolved_records": sum(row["review_status"] == "unresolved" for row in records),
            "reconciliation_passed": len(records) == quality["flagged_records"],
        },
        "duplicate_uuid_groups": groups,
        "records": records,
    }


__all__ = ["TRIAGE_SCHEMA_VERSION", "duplicate_groups", "review_payload", "summary_counts"]
