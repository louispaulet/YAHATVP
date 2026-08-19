"""Public response mappers for the age-analysis bridge queries."""

from __future__ import annotations

import json
from typing import Any

from aggregate_payloads import row_value, snapshot_payload


def _json_object(row: Any, key: str) -> dict[str, Any]:
    value = json.loads(row_value(row, key))
    return value if isinstance(value, dict) else {}


def _json_array(row: Any, key: str) -> list[dict[str, Any]]:
    value = json.loads(row_value(row, key))
    return value if isinstance(value, list) else []


def _person(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "personKey": item.get("person_key"),
        "primaryUuid": item.get("primary_uuid"),
        "firstName": item.get("prenom"),
        "lastName": item.get("nom"),
        "dateOfBirth": item.get("date_naissance"),
        "ageYears": item.get("age_years"),
        "qualityStatus": item.get("date_naissance_quality_status"),
        "declarationCount": int(item.get("declaration_count", 0) or 0),
    }


def simple_analysis_payload(row: Any) -> dict[str, Any]:
    """Map the simple-analysis aggregate into its stable public shape."""

    leaders = _json_object(row, "leaders_json")
    return {
        **snapshot_payload(row),
        "referenceDate": leaders.get("reference_date"),
        "youngest": [_leader(item) for item in leaders.get("youngest", [])],
        "oldest": [_leader(item) for item in leaders.get("oldest", [])],
        "ageBins": [_age_bin(item) for item in _json_array(row, "age_bins_json")],
    }


def _leader(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "declarationUuid": item.get("declaration_uuid"),
        "firstName": item.get("prenom"),
        "lastName": item.get("nom"),
        "dateOfBirth": item.get("date_naissance"),
        "ageYears": int(item.get("age_years", 0) or 0),
        "qualityStatus": item.get("date_naissance_quality_status"),
        "mandate": item.get("mandat_label"),
        "organ": item.get("organ_label"),
    }


def _age_bin(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": item.get("label"),
        "ageBinStart": int(item.get("age_bin_start", 0) or 0),
        "rows": int(item.get("row_count", 0) or 0),
        "averageSalary": float(item.get("average_value", 0) or 0),
        "medianSalary": float(item.get("median_value", 0) or 0),
    }


def age_analysis_payload(row: Any) -> dict[str, Any]:
    """Map one declarant's income, occupation, and asset timelines."""

    return {
        **snapshot_payload(row),
        "person": _person(_json_object(row, "person_json")),
        "matches": [_person(item) for item in _json_array(row, "matches_json")],
        "incomeByYear": [_income_year(item) for item in _json_array(row, "income_json")],
        "occupationsByYear": [
            _occupation_year(item) for item in _json_array(row, "occupations_json")
        ],
        "assetTimeline": [_asset_year(item) for item in _json_array(row, "assets_json")],
    }


def _income_year(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "year": int(item.get("year", 0) or 0),
        "combinedAmount": float(item.get("combined_amount", 0) or 0),
        "sources": [
            {
                "source": source.get("source_label"),
                "label": source.get("income_label"),
                "amount": float(source.get("amount", 0) or 0),
            }
            for source in item.get("sources", [])
        ],
    }


def _occupation_year(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "year": int(item.get("year", 0) or 0),
        "count": int(item.get("occupation_count", 0) or 0),
        "occupations": [
            {
                "label": occupation.get("label"),
                "source": occupation.get("source"),
                "rows": int(occupation.get("row_count", 0) or 0),
            }
            for occupation in item.get("occupations", [])
        ],
    }


def _asset_year(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "year": int(item.get("year", 0) or 0),
        "relativeAge": int(item.get("relative_age", 0) or 0),
        "assets": [
            {
                "source": asset.get("source_section"),
                "name": asset.get("asset_name"),
                "value": asset.get("normalized_value"),
            }
            for asset in item.get("assets", [])
        ],
    }


__all__ = ["age_analysis_payload", "simple_analysis_payload"]
