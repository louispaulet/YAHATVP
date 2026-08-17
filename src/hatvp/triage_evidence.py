"""Source-row and persisted-row matching for quality-triage evidence."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from .triage_evidence_helpers import asset_rows, assets_match, name_rows, normal_name


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
        source = name_rows(source, raw_record)
        persisted = name_rows(persisted, raw_record)
        evidence["name_key"] = (
            f"{normal_name(raw_record.get('prenom'))}|{normal_name(raw_record.get('nom'))}"
        )
    elif table_name == "assets":
        source = asset_rows(source, declaration_uuid, raw_record)
        persisted = asset_rows(persisted, declaration_uuid, raw_record)
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
        assets_match(source, persisted, raw_record)
        if table_name == "assets"
        else bool(source and persisted)
    )
    evidence["source_match"] = source_match
    return source_match, evidence


__all__ = ["index_rows", "json_object", "normal_name", "source_evidence"]
