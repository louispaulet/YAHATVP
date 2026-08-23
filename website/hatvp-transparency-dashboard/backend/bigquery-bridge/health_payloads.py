"""Response mapping for the pipeline health dashboard slice."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from aggregate_payloads import parse_array, row_value


def next_monday_0700(now: datetime | None = None) -> str:
    """Return the next Monday 07:00 Europe/Paris as a UTC timestamp."""

    paris = (now or datetime.now(ZoneInfo("Europe/Paris"))).astimezone(ZoneInfo("Europe/Paris"))
    days = (7 - paris.weekday()) % 7
    target = paris.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(days=days)
    if target <= paris:
        target += timedelta(days=7)
    return target.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z")


def health_payload(row: Any, quality: dict[str, Any] | None = None) -> dict[str, Any]:
    """Convert BigQuery JSON aggregates and the GCS quality report to API shape."""

    report = quality or {}
    quality_body = report.get("quality") or {}
    return {
        "snapshotDate": row_value(row, "snapshot_date"),
        "generatedAt": str(row_value(row, "generated_at")),
        "nextIngestionAt": next_monday_0700(),
        "sources": [
            {
                "sourceId": str(item.get("source_id", "unknown")),
                "declarations": int(item.get("declaration_count", 0)),
                "rawDeclarations": int(item.get("raw_declaration_count", 0)),
            }
            for item in parse_array(row_value(row, "sources_json"))
        ],
        "layers": [
            {
                "layer": str(item.get("layer", "unknown")),
                "rows": int(item.get("row_count", 0) or 0),
                "reviewRows": int(item.get("review_rows", 0) or 0),
            }
            for item in parse_array(row_value(row, "layers_json"))
        ],
        "quality": {
            "errors": int(quality_body.get("errors", 0) or 0),
            "warnings": int(quality_body.get("warnings", 0) or 0),
            "flaggedRecords": int(quality_body.get("flagged_records", 0) or 0),
            "regression": bool(quality_body.get("quality_regression", False)),
        },
        "anomalies": [
            {
                "status": str(item.get("status", "unknown")),
                "rows": int(item.get("row_count", 0) or 0),
            }
            for item in parse_array(row_value(row, "anomalies_json"))
        ],
        "anomalyCategories": [
            {
                "category": str(item.get("category", "unknown")),
                "rows": int(item.get("row_count", 0) or 0),
            }
            for item in parse_array(row_value(row, "anomaly_categories_json"))
        ],
    }


__all__ = ["health_payload", "next_monday_0700"]
