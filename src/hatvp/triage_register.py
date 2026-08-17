"""Machine-readable source-linked quality review register builder."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .triage_matching import (
    disposition,
    index_rows,
    json_object,
    normal_name,
    record_fields,
    source_evidence,
)
from .triage_summary import duplicate_groups, review_payload

TRIAGE_SCHEMA_VERSION = "1.0"
REVIEW_DISPOSITIONS = {
    "expected_identity_collision",
    "source_valid_flag",
    "source_consistent_outlier",
    "duplicate_source_identifier",
    "parser_or_source_mismatch",
    "unresolved",
}


def build_review_register(
    *,
    anomalies: list[dict[str, Any]],
    source_tables: dict[str, list[dict[str, Any]]],
    persisted_tables: dict[str, list[dict[str, Any]]],
    fingerprints: dict[str, list[dict[str, Any]]],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    source_indexes = {name: index_rows(rows) for name, rows in source_tables.items()}
    persisted_indexes = {name: index_rows(rows) for name, rows in persisted_tables.items()}
    repeated_groups: defaultdict[tuple[str, str], set[str | None]] = defaultdict(set)
    repeated_counts: Counter[tuple[str, str]] = Counter()
    for anomaly in anomalies:
        if str(anomaly.get("quality_reason", "")).startswith("repeated name"):
            raw = json_object(anomaly.get("raw_record_json"))
            key = (normal_name(raw.get("prenom")), normal_name(raw.get("nom")))
            repeated_groups[key].add(anomaly.get("declaration_uuid"))
            repeated_counts[key] += 1
    occurrences: Counter[tuple[str, str | None, str]] = Counter()
    records: list[dict[str, Any]] = []
    for anomaly in anomalies:
        table = str(anomaly.get("table_name") or "")
        uuid = anomaly.get("declaration_uuid")
        reason = str(anomaly.get("quality_reason") or "")
        raw = json_object(anomaly.get("raw_record_json"))
        key = (table, uuid, reason)
        occurrences[key] += 1
        matched, source = source_evidence(
            raw,
            table,
            uuid,
            source_indexes.get(table, {}),
            persisted_indexes.get(table, {}),
            fingerprints,
            evidence["raw_xml_uri"],
            evidence["raw_xml_sha256"],
        )
        chosen, status, follow_up, notes = disposition(reason, matched, raw, source)
        if chosen not in REVIEW_DISPOSITIONS:
            raise ValueError(f"Unsupported quality-triage disposition: {chosen}")
        if reason.startswith("repeated name"):
            name_key = (normal_name(raw.get("prenom")), normal_name(raw.get("nom")))
            source["distinct_declaration_uuid_count"] = len(repeated_groups[name_key])
            source["repeated_name_group_size"] = repeated_counts[name_key]
        record_index = raw.get("source_item_index") or occurrences[key]
        records.append(
            {
                "review_key": f"{table}:{uuid or 'none'}:{reason}:{occurrences[key]}",
                "table_name": table,
                "declaration_uuid": uuid,
                "record_key": record_index,
                "source_occurrence_index": occurrences[key],
                "source_fields": record_fields(table, raw),
                "quality_reason": reason,
                "disposition": chosen,
                "review_status": status,
                "follow_up_status": follow_up,
                "reviewer_notes": notes,
                "source_evidence": source,
            }
        )
    records.sort(key=lambda row: row["review_key"])
    groups = duplicate_groups(fingerprints)
    return review_payload(records, groups, evidence)
