"""Stable public response shapes for declaration search and XML detail."""

from __future__ import annotations

import json
from typing import Any

from aggregate_payloads import parse_array, row_value, snapshot_payload

PUBLIC_RESULT_KEYS = (
    "declarationUuid",
    "civilite",
    "firstName",
    "lastName",
    "declarationType",
    "mandate",
    "mandateType",
    "mandateCategory",
    "organ",
    "organDeclaration",
    "dateDeposited",
    "isAmended",
)


def search_result_payload(item: dict[str, Any]) -> dict[str, Any]:
    """Map one internal search result to stable public field names."""

    return {
        "declarationUuid": item.get("declaration_uuid"),
        "civilite": item.get("civilite"),
        "firstName": item.get("prenom"),
        "lastName": item.get("nom"),
        "declarationType": item.get("declaration_type_label"),
        "mandate": item.get("mandat_label"),
        "mandateType": item.get("mandat_type_label"),
        "mandateCategory": item.get("mandat_category_label"),
        "organ": item.get("organ_label"),
        "organDeclaration": item.get("organ_declaration_label"),
        "dateDeposited": item.get("date_depot"),
        "isAmended": item.get("declaration_modificative"),
    }


def search_payload(row: Any) -> dict[str, Any]:
    """Convert the bridge's single search row into the public API shape."""

    results = [search_result_payload(item) for item in parse_array(row_value(row, "results_json"))]
    return {**snapshot_payload(row), "results": results, "resultCount": len(results)}


def declaration_payload(row: Any, raw_xml: str) -> dict[str, Any]:
    """Build the declaration detail payload without private columns."""

    return {
        **snapshot_payload(row),
        "declaration": search_result_payload(json.loads(row_value(row, "result_json"))),
        "rawXml": raw_xml,
    }


def public_result_keys() -> tuple[str, ...]:
    """Expose the response contract for lightweight API-shape tests."""

    return PUBLIC_RESULT_KEYS


def has_private_key(payload: dict[str, Any]) -> bool:
    """Detect accidental contact/address keys before a payload leaves the bridge."""

    return any(key in payload for key in ("email", "telephone", "adresse", "address"))


__all__ = [
    "declaration_payload",
    "has_private_key",
    "public_result_keys",
    "search_payload",
    "search_result_payload",
]
