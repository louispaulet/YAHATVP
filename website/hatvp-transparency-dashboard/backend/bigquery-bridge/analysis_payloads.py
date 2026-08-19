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
        "ageBinsIncludingZero": [
            _age_bin(item) for item in _json_array(row, "age_bins_including_zero_json")
        ],
        "zeroSalaryBins": [_count_bin(item) for item in _json_array(row, "zero_salary_bins_json")],
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


def _count_bin(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": item.get("label"),
        "ageBinStart": int(item.get("age_bin_start", 0) or 0),
        "rows": int(item.get("row_count", 0) or 0),
    }


def age_analysis_payload(row: Any) -> dict[str, Any]:
    """Map one declarant's latest declaration families and source stories."""

    return {
        **snapshot_payload(row),
        "person": _person(_json_object(row, "person_json")),
        "matches": [_person(item) for item in _json_array(row, "matches_json")],
        "declarationContext": _declaration_context(_json_object(row, "declaration_context_json")),
        "incomeByYear": [_income_year(item) for item in _json_array(row, "income_json")],
        "assetInventory": [_asset(item) for item in _json_array(row, "assets_json")],
    }


def _declaration_context(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "interestCount": int(item.get("interest_count", 0) or 0),
        "assetCount": int(item.get("asset_count", 0) or 0),
        "latestInterest": _declaration(item.get("latest_interest")),
        "latestAssets": _declaration(item.get("latest_assets")),
        "history": [_declaration(entry) for entry in item.get("history", [])],
    }


def _declaration(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None
    return {
        "declarationUuid": item.get("declaration_uuid"),
        "filedAt": item.get("date_depot"),
        "typeId": item.get("declaration_type_id"),
        "typeLabel": item.get("declaration_type_label"),
        "isAmended": str(item.get("declaration_modificative", "")).casefold()
        in {"true", "1", "oui"},
        "mandate": item.get("mandat_label"),
        "organ": item.get("organ_label"),
        "family": item.get("declaration_family"),
        "isSelected": bool(item.get("is_selected", False)),
        "incomeRows": int(item.get("income_row_count", 0) or 0),
        "assetRows": int(item.get("asset_row_count", 0) or 0),
    }


def _income_year(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "year": int(item.get("year", 0) or 0),
        "combinedAmount": float(item.get("combined_amount", 0) or 0),
        "sources": [_income_source(source) for source in item.get("sources", [])],
    }


def _income_source(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourceId": item.get("source_id"),
        "kind": item.get("source_kind"),
        "sourceSection": item.get("source_section"),
        "label": item.get("label"),
        "employer": item.get("employer"),
        "startDate": item.get("start_date"),
        "endDate": item.get("end_date"),
        "basis": item.get("amount_basis"),
        "amount": float(item.get("amount", 0) or 0),
        "metricEligible": bool(item.get("metric_eligible", True)),
        "reviewStatus": item.get("review_status"),
    }


def _asset(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "sourceId": item.get("source_id"),
        "kind": item.get("kind"),
        "name": item.get("name"),
        "value": float(item["value"]) if item.get("value") is not None else None,
        "eventYear": int(item["event_year"]) if item.get("event_year") is not None else None,
        "eventDateRaw": item.get("event_date_raw"),
        "eventDate": item.get("event_date"),
        "eventPrecision": item.get("event_precision"),
        "eventSourceField": item.get("event_source_field"),
        "eventKind": item.get("event_kind"),
        "ageYears": int(item["age_years"]) if item.get("age_years") is not None else None,
        "ageRangeMin": (
            int(item["age_range_min"]) if item.get("age_range_min") is not None else None
        ),
        "ageRangeMax": (
            int(item["age_range_max"]) if item.get("age_range_max") is not None else None
        ),
        "declaredAt": item.get("declared_at"),
        "metricEligible": bool(item.get("metric_eligible", True)),
        "reviewStatus": item.get("review_status"),
    }


__all__ = ["age_analysis_payload", "simple_analysis_payload"]
