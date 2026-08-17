"""Source-row and persisted-row matching for quality-triage evidence."""

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
        source = _names(source, raw_record)
        persisted = _names(persisted, raw_record)
        evidence["name_key"] = (
            f"{normal_name(raw_record.get('prenom'))}|{normal_name(raw_record.get('nom'))}"
        )
    elif table_name == "assets":
        key = (
            declaration_uuid,
            raw_record.get("source_section"),
            raw_record.get("source_item_index"),
        )
        source = [row for row in source if _asset_key(row) == key]
        persisted = [row for row in persisted if _asset_key(row) == key]
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
    source_match = (
        _match_assets(source, persisted, raw_record)
        if table_name == "assets"
        else bool(source and persisted)
    )
    evidence["source_match"] = source_match
    return source_match, evidence


def _names(rows: list[dict[str, Any]], raw: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if normal_name(row.get("prenom")) == normal_name(raw.get("prenom"))
        and normal_name(row.get("nom")) == normal_name(raw.get("nom"))
    ]


def _asset_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return row.get("declaration_uuid"), row.get("source_section"), row.get("source_item_index")


def _match_assets(
    source: list[dict[str, Any]], persisted: list[dict[str, Any]], raw: dict[str, Any]
) -> bool:
    def equal(row: dict[str, Any]) -> bool:
        return all(
            row.get(field) == raw.get(field)
            for field in ("raw_value", "normalized_value", "asset_name")
        )

    return any(equal(row) and any(equal(saved) for saved in persisted) for row in source)


__all__ = ["index_rows", "json_object", "normal_name", "source_evidence"]
