"""Fixture contracts for the pipeline-health query and response mapping."""

from __future__ import annotations

import json
from datetime import datetime

from health_payloads import health_payload, next_monday_0700
from query_health import build_health_query


class Row(dict):
    """Small mapping fixture compatible with the bridge row accessor."""

    pass


def _row() -> Row:
    return Row(
        snapshot_date="2026-08-23",
        generated_at="2026-08-23T08:00:00Z",
        sources_json=json.dumps(
            [{"source_id": "hatvp_website", "declaration_count": 9, "raw_declaration_count": 12}]
        ),
        layers_json=json.dumps([{"layer": "bronze", "row_count": 20, "review_rows": 0}]),
        anomalies_json=json.dumps([{"status": "active", "row_count": 3}]),
        anomaly_categories_json=json.dumps(
            [
                {"category": "COMP_YOY_CHANGE", "row_count": 5},
                {"category": "PERSON_DOB_IMPLAUSIBLE", "row_count": 2},
            ]
        ),
    )


def test_health_query_covers_all_source_layers_and_registry() -> None:
    query = build_health_query("project", "dataset")

    assert "ingestion_source" in query
    assert "raw_declaration_count" in query
    assert "FROM `project.dataset`.declarations" in query
    assert "silver_declarations" in query
    assert "gold_assets" in query
    assert "anomaly_registry" in query
    assert "anomaly_categories_json" in query
    assert "LIMIT 5" in query


def test_health_payload_maps_layer_source_quality_and_anomaly_values() -> None:
    payload = health_payload(
        _row(),
        {"quality": {"errors": 1, "warnings": 2, "flagged_records": 3, "quality_regression": True}},
    )

    assert payload["sources"] == [
        {"sourceId": "hatvp_website", "declarations": 9, "rawDeclarations": 12}
    ]
    assert payload["layers"][0]["reviewRows"] == 0
    assert payload["quality"]["flaggedRecords"] == 3
    assert payload["anomalies"][0]["status"] == "active"
    assert payload["anomalyCategories"][0] == {"category": "COMP_YOY_CHANGE", "rows": 5}


def test_next_ingestion_skips_a_monday_run_that_already_started() -> None:
    value = next_monday_0700(datetime.fromisoformat("2026-08-24T08:00:00+02:00"))

    assert value.startswith("2026-08-31T05:00:00")
