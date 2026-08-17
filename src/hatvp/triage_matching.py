"""Source matching and review-disposition rules for quality triage."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any


def normal_name(value: Any) -> str:
    return " ".join(str(value or "").split()).casefold()


def json_object(value: Any) -> dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    parsed = json.loads(value)
    if isinstance(parsed, dict):
        return parsed
    raise ValueError("quality anomaly raw_record_json must contain a JSON object")


def index_rows(rows: list[dict[str, Any]]) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    index: defaultdict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        index[(row.get("declaration_uuid"),)].append(row)
    return dict(index)


def source_evidence(
    raw_record: dict[str, Any],
    table_name: str,
    declaration_uuid: str | None,
    source_rows: dict[tuple[Any, ...], list[dict[str, Any]]],
    persisted_rows: dict[tuple[Any, ...], list[dict[str, Any]]],
    fingerprints: dict[str, list[dict[str, Any]]],
    raw_xml_uri: str,
    raw_xml_sha256: str,
) -> tuple[bool, dict[str, Any]]:
    evidence = {
        "raw_xml_uri": raw_xml_uri,
        "raw_xml_sha256": raw_xml_sha256,
        "source_record_found": False,
        "normalized_record_match": False,
        "source_match": False,
    }
    source = source_rows.get((declaration_uuid,), [])
    persisted = persisted_rows.get((declaration_uuid,), [])
    if table_name == "people":
        source = [
            row
            for row in source
            if normal_name(row.get("prenom")) == normal_name(raw_record.get("prenom"))
            and normal_name(row.get("nom")) == normal_name(raw_record.get("nom"))
        ]
        persisted = [
            row
            for row in persisted
            if normal_name(row.get("prenom")) == normal_name(raw_record.get("prenom"))
            and normal_name(row.get("nom")) == normal_name(raw_record.get("nom"))
        ]
        evidence["name_key"] = (
            f"{normal_name(raw_record.get('prenom'))}|{normal_name(raw_record.get('nom'))}"
        )
    elif table_name == "assets":
        key = (
            declaration_uuid,
            raw_record.get("source_section"),
            raw_record.get("source_item_index"),
        )
        source = [
            row
            for row in source
            if (
                row.get("declaration_uuid"),
                row.get("source_section"),
                row.get("source_item_index"),
            )
            == key
        ]
        persisted = [
            row
            for row in persisted
            if (
                row.get("declaration_uuid"),
                row.get("source_section"),
                row.get("source_item_index"),
            )
            == key
        ]
        evidence.update(
            {
                key: raw_record.get(key)
                for key in ("source_section", "source_item_index", "raw_value", "normalized_value")
            }
        )
    elif table_name == "declarations":
        evidence["source_occurrence_count"] = len(fingerprints.get(declaration_uuid or "", []))
        evidence["canonical_xml_sha256"] = [
            row["canonical_xml_sha256"] for row in fingerprints.get(declaration_uuid or "", [])
        ]
        evidence["semantic_xml_sha256"] = [
            row["semantic_xml_sha256"] for row in fingerprints.get(declaration_uuid or "", [])
        ]
    evidence["source_record_found"] = bool(source)
    evidence["normalized_record_match"] = bool(persisted)
    if table_name == "assets":
        source_match = any(
            _asset_match(row, raw_record)
            and any(_asset_match(saved, raw_record) for saved in persisted)
            for row in source
        )
        evidence["raw_value_matches"] = any(
            row.get("raw_value") == raw_record.get("raw_value") for row in source
        )
        evidence["normalized_value_matches"] = any(
            row.get("normalized_value") == raw_record.get("normalized_value") for row in source
        )
    else:
        source_match = bool(source and persisted)
    evidence["source_match"] = source_match
    return source_match, evidence


def _asset_match(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return all(
        left.get(field) == right.get(field)
        for field in ("raw_value", "normalized_value", "asset_name")
    )


def disposition(
    reason: str, source_match: bool, raw_record: dict[str, Any], evidence: dict[str, Any]
) -> tuple[str, str, str, str]:
    if reason.startswith("repeated name") and source_match:
        return (
            "expected_identity_collision",
            "reviewed",
            "none",
            (
                "Distinct source declarations share a normalized name; names are not stable "
                "identity keys."
            ),
        )
    if (
        reason.startswith("duplicate declaration_uuid")
        and source_match
        and evidence.get("source_occurrence_count", 0) > 1
    ):
        semantic = (
            "identical semantic"
            if len(set(evidence.get("semantic_xml_sha256", []))) == 1
            else "conflicting semantic"
        )
        return (
            "duplicate_source_identifier",
            "reviewed",
            "action_required",
            (
                f"The source contains this declaration UUID more than once with {semantic} "
                "content; retain both rows and investigate recurrence."
            ),
        )
    if (
        reason == "negative asset value"
        and source_match
        and raw_record.get("source_section") == "comptesBancaireDto"
        and isinstance(raw_record.get("normalized_value"), (int, float))
        and raw_record["normalized_value"] < 0
    ):
        return (
            "source_valid_flag",
            "reviewed",
            "monitor",
            (
                "The raw XML contains the same small negative current-account value, consistent "
                "with an overdraft; retain the quality flag."
            ),
        )
    if reason.startswith("robust statistical asset outlier") and source_match:
        return (
            "source_consistent_outlier",
            "reviewed",
            "monitor",
            (
                "The raw XML and persisted normalized asset row agree; the value remains a "
                "descriptive statistical review flag."
            ),
        )
    return (
        "parser_or_source_mismatch",
        "unresolved",
        "action_required",
        "The quality anomaly could not be matched to the expected source-linked record.",
    )


def record_fields(table_name: str, raw_record: dict[str, Any]) -> dict[str, Any]:
    fields = {key: raw_record.get(key) for key in ("source_section", "source_item_index")}
    fields.update(
        {
            key: raw_record.get(key)
            for key in (
                ("prenom", "nom")
                if table_name == "people"
                else ("asset_name", "raw_value", "normalized_value")
                if table_name == "assets"
                else ("date_depot", "declaration_type_id")
                if table_name == "declarations"
                else ()
            )
        }
    )
    return {key: value for key, value in fields.items() if value is not None}
