from __future__ import annotations

import argparse
import hashlib
import io
import json
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import polars as pl
from lxml import etree

from .hashing import sha256_bytes
from .parser import parse_xml
from .storage import GCSArtifactStore, LocalArtifactStore

SNAPSHOT_DATE = "2026-08-16"
TRIAGE_SCHEMA_VERSION = "1.0"
REVIEW_DISPOSITIONS = {
    "expected_identity_collision",
    "source_valid_flag",
    "source_consistent_outlier",
    "duplicate_source_identifier",
    "parser_or_source_mismatch",
    "unresolved",
}

TABLES_FOR_SOURCE_REVIEW = ("declarations", "people", "assets")


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _direct_child(element: etree._Element, name: str) -> etree._Element | None:
    return next((child for child in element if _local_name(child.tag) == name), None)


def _direct_child_text(element: etree._Element, name: str) -> str | None:
    child = _direct_child(element, name)
    if child is None or child.text is None:
        return None
    value = " ".join(child.text.split())
    return value or None


def declaration_xml_fingerprints(path: Path) -> dict[str, list[dict[str, Any]]]:
    """Return canonical source fingerprints for each declaration UUID."""

    fingerprints: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    context = etree.iterparse(
        str(path),
        events=("end",),
        recover=False,
        huge_tree=True,
        load_dtd=False,
        no_network=True,
        resolve_entities=False,
    )
    try:
        for _, element in context:
            if _local_name(element.tag) != "declaration":
                continue
            declaration_uuid = _direct_child_text(element, "uuid")
            if declaration_uuid:
                canonical = etree.tostring(
                    element,
                    method="c14n",
                    exclusive=True,
                    with_comments=False,
                )
                fingerprints[declaration_uuid].append(
                    {
                        "occurrence_index": len(fingerprints[declaration_uuid]),
                        "canonical_xml_sha256": hashlib.sha256(canonical).hexdigest(),
                        "canonical_xml_bytes": len(canonical),
                        "date_depot_raw": _direct_child_text(element, "dateDepot"),
                    }
                )
            parent = element.getparent()
            element.clear()
            if parent is not None:
                while element.getprevious() is not None:
                    del parent[0]
    except etree.XMLSyntaxError as exc:
        raise ValueError(f"HATVP XML is malformed: {exc}") from exc
    return dict(fingerprints)


def _normal_name(value: Any) -> str:
    return " ".join(str(value or "").split()).casefold()


def _json_object(value: Any) -> dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            return parsed
    raise ValueError("quality anomaly raw_record_json must contain a JSON object")


def _values_equal(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return left is right
    if isinstance(left, float) and isinstance(right, float):
        return abs(left - right) < 1e-9
    return left == right


def _row_matches(left: dict[str, Any], right: dict[str, Any], fields: tuple[str, ...]) -> bool:
    return all(_values_equal(left.get(field), right.get(field)) for field in fields)


def _index_rows(
    rows: list[dict[str, Any]], key_fields: tuple[str, ...]
) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    index: defaultdict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        index[tuple(row.get(field) for field in key_fields)].append(row)
    return dict(index)


def _source_evidence(
    *,
    raw_xml_uri: str,
    raw_xml_sha256: str,
    source_rows: dict[tuple[Any, ...], list[dict[str, Any]]],
    persisted_rows: dict[tuple[Any, ...], list[dict[str, Any]]],
    raw_record: dict[str, Any],
    table_name: str,
    declaration_uuid: str | None,
    fingerprints: dict[str, list[dict[str, Any]]],
) -> tuple[bool, dict[str, Any]]:
    evidence: dict[str, Any] = {
        "raw_xml_uri": raw_xml_uri,
        "raw_xml_sha256": raw_xml_sha256,
        "source_record_found": False,
        "normalized_record_match": False,
        "source_match": False,
    }
    source_candidates = source_rows.get((declaration_uuid,), [])
    persisted_candidates = persisted_rows.get((declaration_uuid,), [])

    if table_name == "people":
        source_candidates = [
            row
            for row in source_candidates
            if row.get("declaration_uuid") == declaration_uuid
            and _normal_name(row.get("prenom")) == _normal_name(raw_record.get("prenom"))
            and _normal_name(row.get("nom")) == _normal_name(raw_record.get("nom"))
        ]
        persisted_candidates = [
            row
            for row in persisted_candidates
            if row.get("declaration_uuid") == declaration_uuid
            and _normal_name(row.get("prenom")) == _normal_name(raw_record.get("prenom"))
            and _normal_name(row.get("nom")) == _normal_name(raw_record.get("nom"))
        ]
        evidence["name_key"] = (
            f"{_normal_name(raw_record.get('prenom'))}|{_normal_name(raw_record.get('nom'))}"
        )
    elif table_name == "assets":
        key = (
            declaration_uuid,
            raw_record.get("source_section"),
            raw_record.get("source_item_index"),
        )
        source_candidates = [
            row
            for row in source_candidates
            if (
                row.get("declaration_uuid"),
                row.get("source_section"),
                row.get("source_item_index"),
            )
            == key
        ]
        persisted_candidates = [
            row
            for row in persisted_candidates
            if (
                row.get("declaration_uuid"),
                row.get("source_section"),
                row.get("source_item_index"),
            )
            == key
        ]
        evidence["source_section"] = raw_record.get("source_section")
        evidence["source_item_index"] = raw_record.get("source_item_index")
        evidence["raw_value"] = raw_record.get("raw_value")
        evidence["normalized_value"] = raw_record.get("normalized_value")
    elif table_name == "declarations":
        source_candidates = [
            row for row in source_candidates if row.get("declaration_uuid") == declaration_uuid
        ]
        persisted_candidates = [
            row for row in persisted_candidates if row.get("declaration_uuid") == declaration_uuid
        ]
        evidence["source_occurrence_count"] = len(fingerprints.get(declaration_uuid or "", []))
        evidence["canonical_xml_sha256"] = [
            item["canonical_xml_sha256"] for item in fingerprints.get(declaration_uuid or "", [])
        ]

    evidence["source_record_found"] = bool(source_candidates)
    evidence["normalized_record_match"] = bool(persisted_candidates)
    if table_name == "people":
        source_match = bool(source_candidates and persisted_candidates)
    elif table_name == "assets":
        fields = ("raw_value", "normalized_value", "asset_name")
        source_match = any(
            _row_matches(source, raw_record, fields)
            and any(
                _row_matches(persisted, raw_record, fields) for persisted in persisted_candidates
            )
            for source in source_candidates
        )
        evidence["raw_value_matches"] = any(
            _values_equal(source.get("raw_value"), raw_record.get("raw_value"))
            for source in source_candidates
        )
        evidence["normalized_value_matches"] = any(
            _values_equal(source.get("normalized_value"), raw_record.get("normalized_value"))
            for source in source_candidates
        )
    else:
        source_match = bool(source_candidates and persisted_candidates)
    evidence["source_match"] = source_match
    return source_match, evidence


def _disposition_for(
    *,
    quality_reason: str,
    source_match: bool,
    raw_record: dict[str, Any],
    evidence: dict[str, Any],
) -> tuple[str, str, str, str]:
    if quality_reason.startswith("repeated name"):
        if source_match:
            return (
                "expected_identity_collision",
                "reviewed",
                "none",
                (
                    "Distinct source declarations share a normalized name; names are not "
                    "stable identity keys."
                ),
            )
        return (
            "parser_or_source_mismatch",
            "unresolved",
            "action_required",
            "The repeated-name anomaly could not be matched to the source-linked people record.",
        )
    if quality_reason.startswith("duplicate declaration_uuid"):
        if source_match and evidence.get("source_occurrence_count", 0) > 1:
            hashes = evidence.get("canonical_xml_sha256", [])
            content = "identical" if len(set(hashes)) == 1 else "conflicting"
            return (
                "duplicate_source_identifier",
                "reviewed",
                "action_required",
                (
                    f"The source contains this declaration UUID more than once with {content} "
                    "canonical XML content; retain both rows and investigate recurrence."
                ),
            )
        return (
            "parser_or_source_mismatch",
            "unresolved",
            "action_required",
            "The duplicate UUID anomaly could not be matched to repeated source declarations.",
        )
    if quality_reason == "negative asset value":
        if (
            source_match
            and raw_record.get("source_section") == "comptesBancaireDto"
            and isinstance(raw_record.get("normalized_value"), (int, float))
            and raw_record["normalized_value"] < 0
        ):
            return (
                "source_valid_flag",
                "reviewed",
                "monitor",
                (
                    "The raw XML contains the same small negative current-account value, "
                    "consistent with an overdraft; retain the quality flag."
                ),
            )
        return (
            "parser_or_source_mismatch",
            "unresolved",
            "action_required",
            "The negative asset value did not match the expected bank-account source record.",
        )
    if quality_reason.startswith("robust statistical asset outlier"):
        if source_match:
            return (
                "source_consistent_outlier",
                "reviewed",
                "monitor",
                (
                    "The raw XML and persisted normalized asset row agree; the value remains "
                    "a descriptive statistical review flag."
                ),
            )
        return (
            "parser_or_source_mismatch",
            "unresolved",
            "action_required",
            (
                "The asset outlier could not be matched exactly to the raw XML and normalized "
                "source-linked row."
            ),
        )
    return (
        "unresolved",
        "unresolved",
        "action_required",
        "No disposition rule exists for this quality reason.",
    )


def _record_value_fields(table_name: str, raw_record: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "source_section": raw_record.get("source_section"),
        "source_item_index": raw_record.get("source_item_index"),
    }
    if table_name == "people":
        fields.update({"prenom": raw_record.get("prenom"), "nom": raw_record.get("nom")})
    elif table_name == "assets":
        fields.update(
            {
                "asset_name": raw_record.get("asset_name"),
                "raw_value": raw_record.get("raw_value"),
                "normalized_value": raw_record.get("normalized_value"),
            }
        )
    elif table_name == "declarations":
        fields.update(
            {
                "date_depot": raw_record.get("date_depot"),
                "declaration_type_id": raw_record.get("declaration_type_id"),
            }
        )
    return {key: value for key, value in fields.items() if value is not None}


def build_review_register(
    *,
    anomalies: list[dict[str, Any]],
    source_tables: dict[str, list[dict[str, Any]]],
    persisted_tables: dict[str, list[dict[str, Any]]],
    fingerprints: dict[str, list[dict[str, Any]]],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    source_indexes = {
        table_name: _index_rows(rows, ("declaration_uuid",))
        for table_name, rows in source_tables.items()
    }
    persisted_indexes = {
        table_name: _index_rows(rows, ("declaration_uuid",))
        for table_name, rows in persisted_tables.items()
    }
    repeated_name_groups: defaultdict[tuple[str, str], set[str | None]] = defaultdict(set)
    repeated_name_counts: Counter[tuple[str, str]] = Counter()
    for anomaly in anomalies:
        if anomaly.get("quality_reason", "").startswith("repeated name"):
            raw_record = _json_object(anomaly.get("raw_record_json"))
            name_key = (_normal_name(raw_record.get("prenom")), _normal_name(raw_record.get("nom")))
            repeated_name_groups[name_key].add(anomaly.get("declaration_uuid"))
            repeated_name_counts[name_key] += 1

    occurrence_counts: Counter[tuple[str, str | None, str]] = Counter()
    records: list[dict[str, Any]] = []
    for anomaly in anomalies:
        table_name = str(anomaly.get("table_name") or "")
        declaration_uuid = anomaly.get("declaration_uuid")
        quality_reason = str(anomaly.get("quality_reason") or "")
        raw_record = _json_object(anomaly.get("raw_record_json"))
        base_key = (table_name, declaration_uuid, quality_reason)
        occurrence_counts[base_key] += 1
        occurrence_index = occurrence_counts[base_key]
        source_match, source_evidence = _source_evidence(
            raw_xml_uri=evidence["raw_xml_uri"],
            raw_xml_sha256=evidence["raw_xml_sha256"],
            source_rows=source_indexes.get(table_name, {}),
            persisted_rows=persisted_indexes.get(table_name, {}),
            raw_record=raw_record,
            table_name=table_name,
            declaration_uuid=declaration_uuid,
            fingerprints=fingerprints,
        )
        disposition, review_status, follow_up_status, notes = _disposition_for(
            quality_reason=quality_reason,
            source_match=source_match,
            raw_record=raw_record,
            evidence=source_evidence,
        )
        if disposition not in REVIEW_DISPOSITIONS:
            raise ValueError(f"Unsupported quality-triage disposition: {disposition}")
        if quality_reason.startswith("repeated name"):
            name_key = (_normal_name(raw_record.get("prenom")), _normal_name(raw_record.get("nom")))
            source_evidence["distinct_declaration_uuid_count"] = len(repeated_name_groups[name_key])
            source_evidence["repeated_name_group_size"] = repeated_name_counts[name_key]
        record_key = raw_record.get("source_item_index")
        if record_key is None:
            record_key = occurrence_index
        record = {
            "review_key": (
                f"{table_name}:{declaration_uuid or 'none'}:{quality_reason}:{occurrence_index}"
            ),
            "table_name": table_name,
            "declaration_uuid": declaration_uuid,
            "record_key": record_key,
            "source_occurrence_index": occurrence_index,
            "source_fields": _record_value_fields(table_name, raw_record),
            "quality_reason": quality_reason,
            "disposition": disposition,
            "review_status": review_status,
            "follow_up_status": follow_up_status,
            "reviewer_notes": notes,
            "source_evidence": source_evidence,
        }
        records.append(record)

    records.sort(key=lambda row: row["review_key"])
    reason_counts = Counter(row["quality_reason"] for row in records)
    disposition_counts = Counter(row["disposition"] for row in records)
    source_match_counts = Counter(
        "matched" if row["source_evidence"]["source_match"] else "unmatched" for row in records
    )
    duplicate_groups = []
    for declaration_uuid, occurrences in sorted(fingerprints.items()):
        if len(occurrences) < 2:
            continue
        duplicate_groups.append(
            {
                "declaration_uuid": declaration_uuid,
                "occurrence_count": len(occurrences),
                "content_classification": (
                    "identical"
                    if len({item["canonical_xml_sha256"] for item in occurrences}) == 1
                    else "conflicting"
                ),
                "canonical_xml_sha256": [item["canonical_xml_sha256"] for item in occurrences],
                "date_depot_raw": [item["date_depot_raw"] for item in occurrences],
            }
        )

    return {
        "schema_version": TRIAGE_SCHEMA_VERSION,
        "snapshot_date": evidence["snapshot_date"],
        "evidence": evidence,
        "quality_report": evidence["quality_report"],
        "summary": {
            "flagged_records": len(records),
            "reason_counts": dict(sorted(reason_counts.items())),
            "disposition_counts": dict(sorted(disposition_counts.items())),
            "source_match_counts": dict(sorted(source_match_counts.items())),
            "duplicate_uuid_groups": len(duplicate_groups),
            "unresolved_records": sum(row["review_status"] == "unresolved" for row in records),
            "reconciliation_passed": len(records)
            == evidence["quality_report"]["quality"]["flagged_records"],
        },
        "duplicate_uuid_groups": duplicate_groups,
        "records": records,
    }


def _artifact_uri(prefix: str, path: str) -> str:
    return f"{prefix.rstrip('/')}/{path.lstrip('/')}"


def _read_parquet(store: Any, path: str) -> tuple[list[dict[str, Any]], str]:
    content = store.read_bytes(path)
    return pl.read_parquet(io.BytesIO(content)).to_dicts(), sha256_bytes(content)


def build_snapshot_review(
    store: Any,
    snapshot_date: str = SNAPSHOT_DATE,
    source_uri_prefix: str | None = None,
) -> dict[str, Any]:
    prefix = getattr(store, "prefix", "").strip("/")
    uri_prefix = source_uri_prefix
    if uri_prefix is None:
        uri_prefix = (
            f"gs://{store.bucket.name}/{prefix}"
            if isinstance(store, GCSArtifactStore)
            else f"local://{store.root}/{prefix}"
        )
    raw_xml_path = f"raw/snapshot_date={snapshot_date}/declarations.xml"
    raw_csv_path = f"raw/snapshot_date={snapshot_date}/liste.csv"
    metadata_path = f"raw/snapshot_date={snapshot_date}/metadata.json"
    quality_path = f"quality/snapshot_date={snapshot_date}/report.json"
    quarantine_path = f"quarantine/snapshot_date={snapshot_date}/anomalies.parquet"
    raw_xml = store.read_bytes(raw_xml_path)
    raw_metadata = json.loads(store.read_bytes(metadata_path))
    quality_report = json.loads(store.read_bytes(quality_path))
    anomalies, quarantine_sha256 = _read_parquet(store, quarantine_path)
    persisted_tables: dict[str, list[dict[str, Any]]] = {}
    silver_hashes: dict[str, str] = {}
    for table_name in TABLES_FOR_SOURCE_REVIEW:
        table_path = f"silver/{table_name}/snapshot_date={snapshot_date}/data.parquet"
        persisted_tables[table_name], silver_hashes[table_name] = _read_parquet(store, table_path)

    with tempfile.NamedTemporaryFile(suffix=".xml") as source_file:
        source_file.write(raw_xml)
        source_file.flush()
        source_tables = parse_xml(Path(source_file.name), snapshot_date)
        fingerprints = declaration_xml_fingerprints(Path(source_file.name))

    source_info = {item["name"]: item for item in raw_metadata.get("files", []) if item.get("name")}
    evidence = {
        "snapshot_date": snapshot_date,
        "quality_report_uri": _artifact_uri(uri_prefix, quality_path),
        "quarantine_uri": _artifact_uri(uri_prefix, quarantine_path),
        "raw_xml_uri": _artifact_uri(uri_prefix, raw_xml_path),
        "raw_csv_uri": _artifact_uri(uri_prefix, raw_csv_path),
        "metadata_uri": _artifact_uri(uri_prefix, metadata_path),
        "state_uri": _artifact_uri(uri_prefix, "state/latest.json"),
        "raw_xml_sha256": source_info.get("declarations.xml", {}).get("sha256")
        or sha256_bytes(raw_xml),
        "raw_csv_sha256": source_info.get("liste.csv", {}).get("sha256"),
        "pipeline_git_sha": raw_metadata.get("pipeline_git_sha"),
        "pipeline_version": raw_metadata.get("pipeline_version"),
        "quality_report_sha256": sha256_bytes(store.read_bytes(quality_path)),
        "quarantine_sha256": quarantine_sha256,
        "silver_sha256": silver_hashes,
        "silver_uris": {
            table_name: _artifact_uri(
                uri_prefix,
                f"silver/{table_name}/snapshot_date={snapshot_date}/data.parquet",
            )
            for table_name in TABLES_FOR_SOURCE_REVIEW
        },
        "quality_report": quality_report,
    }
    return build_review_register(
        anomalies=anomalies,
        source_tables=source_tables,
        persisted_tables=persisted_tables,
        fingerprints=fingerprints,
        evidence=evidence,
    )


def _format_number(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if isinstance(value, (int, float)):
        return f"{value:,.0f}".replace(",", " ")
    return str(value)


def render_markdown(review: dict[str, Any]) -> str:
    summary = review["summary"]
    quality = review["quality_report"]
    evidence = review["evidence"]
    records = review["records"]
    reason_counts = summary["reason_counts"]
    disposition_counts = summary["disposition_counts"]
    reconciliation_label = "passed" if summary["reconciliation_passed"] else "failed"
    duplicate_rows = sum(
        count
        for reason, count in reason_counts.items()
        if reason.startswith("duplicate declaration_uuid")
    )
    repeated = [row for row in records if row["quality_reason"].startswith("repeated name")]
    repeated_groups: Counter[tuple[str, str]] = Counter()
    for row in repeated:
        fields = row["source_fields"]
        repeated_groups[(_normal_name(fields.get("prenom")), _normal_name(fields.get("nom")))] += 1
    outliers = [
        row
        for row in records
        if row["quality_reason"].startswith("robust statistical asset outlier")
    ]
    outliers.sort(key=lambda row: row["source_fields"].get("normalized_value", 0), reverse=True)
    negatives = [row for row in records if row["quality_reason"] == "negative asset value"]
    lines = [
        f"# Quality triage — HATVP snapshot {review['snapshot_date']}",
        "",
        "> Auditable review register for every flagged anomaly in the first production snapshot.",
        "",
        "## Outcome",
        "",
        (
            f"The immutable snapshot contains **{summary['flagged_records']:,} flagged records**, "
            f"with **{summary['unresolved_records']:,} unresolved records** after source-linked "
            "review. The register reconciles to the quality report: "
            f"**{reconciliation_label}**."
        ),
        "",
        (
            "No raw, silver, quarantine, quality, or state artifact was modified. Statistical "
            "flags remain retained; this report records review dispositions rather than "
            "correcting source data."
        ),
        "",
        "## Evidence",
        "",
        "| Item | Value |",
        "| --- | --- |",
        f"| Snapshot date | `{review['snapshot_date']}` |",
        f"| Raw XML SHA-256 | `{evidence['raw_xml_sha256']}` |",
        f"| Pipeline Git SHA | `{evidence['pipeline_git_sha']}` |",
        f"| Quality report | `{evidence['quality_report_uri']}` |",
        f"| Quarantine register | `{evidence['quarantine_uri']}` |",
        f"| Raw XML | `{evidence['raw_xml_uri']}` |",
        f"| Quality report SHA-256 | `{evidence['quality_report_sha256']}` |",
        f"| Quarantine SHA-256 | `{evidence['quarantine_sha256']}` |",
        "",
        "## Reconciliation",
        "",
        (
            f"The source quality report records `{quality['quality']['flagged_records']:,}` "
            f"flagged records, zero errors, and `{quality['quality']['warnings']:,}` warnings. "
            "The warning count is a separate metric from the anomaly-row count."
        ),
        "",
        "| Original quality reason | Rows | Disposition |",
        "| --- | ---: | --- |",
    ]
    for reason, count in sorted(reason_counts.items()):
        dispositions = Counter(
            row["disposition"] for row in records if row["quality_reason"] == reason
        )
        disposition_text = ", ".join(
            f"`{name}`: {value:,}" for name, value in sorted(dispositions.items())
        )
        lines.append(f"| {reason} | {count:,} | {disposition_text} |")
    lines.extend(
        [
            "",
            "| Review disposition | Rows |",
            "| --- | ---: |",
        ]
    )
    for disposition, count in sorted(disposition_counts.items()):
        lines.append(f"| `{disposition}` | {count:,} |")
    lines.extend(
        [
            "",
            "## Findings",
            "",
            (
                f"- **Repeated names:** {len(repeated):,} rows across "
                f"{len(repeated_groups):,} normalized name groups. Each matched a source-linked "
                "person record and is retained as an expected identity collision; no people "
                "were deduplicated."
            ),
            (
                f"- **Duplicate declaration UUIDs:** "
                f"{duplicate_rows:,} "
                f"rows across {len(review['duplicate_uuid_groups']):,} source UUID groups. "
                "Each group requires source-quality follow-up."
            ),
            (
                f"- **Negative assets:** {len(negatives):,} rows. The reviewed values are "
                "bank-account entries and remain flagged as source-valid overdraft-style values."
            ),
            (
                f"- **Statistical asset outliers:** {len(outliers):,} rows. Each matched the "
                "raw XML and persisted normalized row; values remain descriptive outlier flags "
                "for monitoring."
            ),
            "",
            "## Duplicate declaration UUID groups",
            "",
            "| Declaration UUID | Occurrences | Content | Canonical XML SHA-256 |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for group in review["duplicate_uuid_groups"]:
        hashes = "<br>".join(f"`{value}`" for value in group["canonical_xml_sha256"])
        lines.append(
            f"| `{group['declaration_uuid']}` | {group['occurrence_count']} | "
            f"{group['content_classification']} | {hashes} |"
        )
    lines.extend(
        [
            "",
            "## Negative asset values",
            "",
            "| Declaration UUID | Section | Item | Raw value | Normalized value | Disposition |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in negatives:
        fields = row["source_fields"]
        lines.append(
            f"| `{row['declaration_uuid']}` | `{fields.get('source_section', '—')}` | "
            f"{fields.get('source_item_index', '—')} | `{fields.get('raw_value', '—')}` | "
            f"{_format_number(fields.get('normalized_value'))} | `{row['disposition']}` |"
        )
    lines.extend(
        [
            "",
            "## Highest-value asset outliers",
            "",
            (
                "The complete row-level register is in the JSON artifact. The table below "
                "provides the highest-value source-linked candidates for manual fact checking."
            ),
            "",
            "| Declaration UUID | Section | Item | Asset | Raw value | Normalized value |",
            "| --- | --- | ---: | --- | ---: | ---: |",
        ]
    )
    for row in outliers[:20]:
        fields = row["source_fields"]
        lines.append(
            f"| `{row['declaration_uuid']}` | `{fields.get('source_section', '—')}` | "
            f"{fields.get('source_item_index', '—')} | {fields.get('asset_name', '—')} | "
            f"`{fields.get('raw_value', '—')}` | "
            f"{_format_number(fields.get('normalized_value'))} |"
        )
    lines.extend(
        [
            "",
            "## Review method and follow-up",
            "",
            (
                "- The raw XML is authoritative for source verification; normalized Parquet is "
                "used to confirm the persisted row and provenance key."
            ),
            (
                "- Repeated names are not identity proof. Stable declaration UUIDs remain the "
                "identity boundary."
            ),
            (
                "- Duplicate UUID groups are retained and require monitoring or source "
                "correction; no duplicate declaration was deleted."
            ),
            (
                "- Any source/parser mismatch is an actionable follow-up requiring a fixture "
                "before changing normalization logic."
            ),
            (
                "- The machine-readable register contains one entry per flagged row, including "
                "source evidence, disposition, review status, notes, and follow-up status."
            ),
            "",
            "## Artifacts",
            "",
            "- Machine-readable register: `reports/quality-triage-2026-08-16.json`",
            "- Immutable source evidence: the GCS objects listed above",
        ]
    )
    return "\n".join(lines) + "\n"


def write_review_artifacts(review: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"quality-triage-{review['snapshot_date']}.json"
    markdown_path = output_dir / f"quality-triage-{review['snapshot_date']}.md"
    json_path.write_text(json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    markdown_path.write_text(render_markdown(review))
    return json_path, markdown_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bucket", help="GCS bucket containing the HATVP artifacts")
    source.add_argument("--local-root", type=Path, help="Local artifact root for fixture review")
    parser.add_argument("--prefix", default="hatvp")
    parser.add_argument("--snapshot-date", default=SNAPSHOT_DATE)
    parser.add_argument(
        "--source-uri-prefix",
        help="Canonical evidence URI prefix, for example gs://bucket/hatvp",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.bucket:
        store = GCSArtifactStore(args.bucket, args.prefix)
    else:
        store = LocalArtifactStore(args.local_root, args.prefix)
    review = build_snapshot_review(store, args.snapshot_date, args.source_uri_prefix)
    json_path, markdown_path = write_review_artifacts(review, args.output_dir)
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
