"""Review-disposition rules and compatibility exports for triage matching."""

from __future__ import annotations

from typing import Any

from .triage_evidence import index_rows, json_object, normal_name, source_evidence


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
    names = (
        ("prenom", "nom")
        if table_name == "people"
        else ("asset_name", "raw_value", "normalized_value")
        if table_name == "assets"
        else ("date_depot", "declaration_type_id")
        if table_name == "declarations"
        else ()
    )
    fields.update({key: raw_record.get(key) for key in names})
    return {key: value for key, value in fields.items() if value is not None}


__all__ = [
    "disposition",
    "index_rows",
    "json_object",
    "normal_name",
    "record_fields",
    "source_evidence",
]
