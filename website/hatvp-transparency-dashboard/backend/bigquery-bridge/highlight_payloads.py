"""Public response mapping for editorial dashboard highlights."""

from __future__ import annotations

from typing import Any

from aggregate_payloads import parse_array, row_value, snapshot_payload


def _base(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "declarationUuid": item.get("declaration_uuid"),
        "firstName": item.get("prenom"),
        "lastName": item.get("nom"),
        "mandate": item.get("mandat_label"),
    }


def highlights_payload(row: Any) -> dict[str, Any]:
    """Convert the three BigQuery arrays into a stable public JSON contract."""

    payload = snapshot_payload(row)
    payload["incomeChanges"] = [
        {
            **_base(item),
            "fromYear": int(item["previous_year"]),
            "toYear": int(item["income_year"]),
            "fromAmount": float(item["previous_amount"] or 0),
            "toAmount": float(item["amount"] or 0),
            "absoluteChange": float(item["absolute_change"] or 0),
            "ratio": float(item["ratio"]) if item.get("ratio") is not None else None,
            "reviewRequired": bool(item.get("review_required")),
        }
        for item in parse_array(row_value(row, "income_changes_json"))
    ]
    payload["unusualAssets"] = [
        {
            **_base(item),
            "section": item.get("source_section"),
            "assetName": item.get("asset_name"),
            "rawValue": item.get("raw_value"),
            "amount": float(item["normalized_value"] or 0),
            "anomalyStatus": item.get("anomaly_status"),
            "reviewRequired": bool(item.get("review_required")),
        }
        for item in parse_array(row_value(row, "unusual_assets_json"))
    ]
    payload["amendedRecords"] = [
        {
            **_base(item),
            "filingCount": int(item.get("filing_count", 0)),
            "amendedCount": int(item.get("amended_count", 0)),
            "firstFiled": item.get("first_filed"),
            "latestFiled": item.get("latest_filed"),
        }
        for item in parse_array(row_value(row, "amended_records_json"))
    ]
    return payload


__all__ = ["highlights_payload"]
