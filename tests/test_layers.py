"""Unit coverage for HATVP Silver anomaly, registry, and Gold contracts."""

from __future__ import annotations

import json

from hatvp.layers.anomaly import anomaly_rule_ids, detect_anomalies
from hatvp.layers.gold import build_gold, gold_metric_rows, latest_declaration_keys
from hatvp.layers.registry import anomaly_id, upsert_registry
from hatvp.layers.silver import apply_registry_states, build_silver
from tests.layers_support import historical_tables, layer_tables


def test_all_required_rules_flag_source_rows_without_rewriting_values() -> None:
    current = layer_tables()
    items = detect_anomalies(current, historical_tables())
    found = {item["rule_id"] for item in items}

    lifecycle = {"ANOMALY_KNOWN", "ANOMALY_REGRESSION"}
    assert set(anomaly_rule_ids()) - lifecycle <= found | {
        "PERSON_IDENTITY_REVIEW",
        "PERSON_DOB_CONFLICT",
    }
    assert current["incomes"][1]["normalized_value"] == 500_000
    assert all(item["source_format"] == "xml" for item in items if item["table_name"] == "incomes")


def test_silver_adds_field_eligibility_registry_links_and_evidence() -> None:
    silver, _, registry = build_silver(
        layer_tables(), historical_tables(), snapshot_date="2026-01-01"
    )
    income_rows = silver["incomes"]
    flagged = next(row for row in income_rows if row["normalized_value"] == 500_000)

    assert flagged["anomaly_active"] is True
    assert flagged["metric_eligible"] is False
    assert json.loads(flagged["field_metric_eligibility_json"])["normalized_value"] is False
    assert json.loads(flagged["anomaly_registry_ids"])
    assert registry and all(row["anomaly_id"].startswith("anomaly_") for row in registry)
    assert json.loads(flagged["anomaly_evidence_json"])[0]["source_format"] == "xml"


def test_registry_is_idempotent_and_preserves_first_seen() -> None:
    current = layer_tables()
    occurrence = detect_anomalies(current, historical_tables())[0]
    first = upsert_registry([occurrence], [], "2026-01-01")
    repeated = upsert_registry([occurrence], first, "2026-01-01")
    later = upsert_registry([occurrence], repeated, "2026-02-01")

    assert len(repeated) == len(first) == len(later) == 1
    assert repeated[0]["occurrence_count"] == 1
    assert later[0]["occurrence_count"] == 2
    assert later[0]["first_seen"] == "2026-01-01"
    assert later[0]["status"] == "known/reported"
    assert anomaly_id(occurrence["anomaly_key"]) == first[0]["anomaly_id"]


def test_amendment_selects_one_latest_declaration_and_child_rows_follow_it() -> None:
    current = layer_tables()
    silver, all_silver, registry = build_silver(current, {}, snapshot_date="2026-01-01")
    gold, updated_registry = build_gold(all_silver, registry)
    gold = apply_registry_states(gold, updated_registry)

    selected = latest_declaration_keys(all_silver["declarations"])
    assert selected == {"new"}
    assert {row["bronze_record_key"] for row in gold["declarations"]} == {"new"}
    assert {row["bronze_record_key"] for row in gold["people"]} == {"new"}
    assert all(row["is_latest_declaration"] for row in gold["declarations"])


def test_latest_gold_metrics_exclude_anomalous_values_but_keep_rows() -> None:
    current = layer_tables()
    silver, all_silver, registry = build_silver(current, {}, snapshot_date="2026-01-01")
    gold, registry = build_gold(all_silver, registry)
    gold = apply_registry_states(gold, registry)
    eligible = gold_metric_rows({"incomes": gold["incomes"]})

    assert gold["incomes"]
    assert all(row["normalized_value"] != 500_000 for row in eligible)
    assert any(row["normalized_value"] == 500_000 for row in gold["incomes"])


def test_resolved_registry_occurrence_is_marked_as_regression() -> None:
    current = layer_tables()
    occurrence = detect_anomalies(current, {})[0]
    existing = upsert_registry([occurrence], [], "2026-01-01")
    existing[0]["status"] = "superseded"
    repeated = detect_anomalies(current, {}, existing)
    assert any(item["rule_id"] == "ANOMALY_REGRESSION" for item in repeated)
    registry = upsert_registry(repeated, existing, "2026-02-01")
    assert any(row["status"] == "regression" for row in registry)


def test_source_anomaly_evidence_keeps_format_values() -> None:
    items = detect_anomalies(layer_tables(), {})
    source = next(item for item in items if item["rule_id"] == "SOURCE_CROSS_FORMAT")
    assert source["evidence"]["values"] == [
        {"format": "xml", "value": "75"},
        {"format": "csv", "value": "13"},
    ]
