"""Regression coverage for configurable DOB checks and registry lifecycle aliases."""

from __future__ import annotations

from typing import Any

from hatvp.layers.anomaly import detect_anomalies
from hatvp.layers.registry import upsert_registry
from hatvp.layers.silver import build_silver
from tests.layers_support import declaration, historical_tables, layer_tables, people


def _people_tables(birth: str) -> dict[str, list[dict[str, Any]]]:
    return {
        "declarations": [declaration("dob", "2026-01-01", "2026-01-01")],
        "people": [people("dob", "2026-01-01", birth)],
        "incomes": [],
        "assets": [],
    }


def test_birth_age_threshold_flags_101_but_not_80_and_keeps_observed_value() -> None:
    old = _people_tables("1925-01-01")
    young = _people_tables("1945-01-01")
    old_items = detect_anomalies(old, {})
    young_items = detect_anomalies(young, {})

    assert any(item["rule_id"] == "PERSON_DOB_IMPLAUSIBLE" for item in old_items)
    assert not any(item["rule_id"] == "PERSON_DOB_IMPLAUSIBLE" for item in young_items)
    assert old["people"][0]["date_naissance"] == "1925-01-01"
    silver, _, _ = build_silver(old, {}, snapshot_date="2026-01-01")
    assert silver["people"][0]["date_naissance"] == "1925-01-01"


def test_birth_age_threshold_can_be_overridden_for_detection() -> None:
    rows = _people_tables("1925-01-01")

    assert not any(
        item["rule_id"] == "PERSON_DOB_IMPLAUSIBLE"
        for item in detect_anomalies(rows, {}, dob_max_age_years=110)
    )


def test_known_occurrence_keeps_original_rule_id_in_registry() -> None:
    current = layer_tables()
    original = next(
        item
        for item in detect_anomalies(current, historical_tables())
        if item["rule_id"] == "PERSON_DOB_IMPLAUSIBLE"
    )
    first = upsert_registry([original], [], "2026-01-01")
    repeated = detect_anomalies(current, historical_tables(), first)
    lifecycle = next(
        item
        for item in repeated
        if item["anomaly_key"] == original["anomaly_key"]
        and item["rule_id"] == "ANOMALY_KNOWN"
        and item["original_rule_id"] == original["rule_id"]
    )
    assert lifecycle["original_rule_id"] == "PERSON_DOB_IMPLAUSIBLE"

    updated = upsert_registry(repeated, first, "2026-02-01")
    row = next(item for item in updated if item["anomaly_key"] == original["anomaly_key"])
    assert row["rule_id"] == "PERSON_DOB_IMPLAUSIBLE"
    assert row["status"] == "known/reported"
    assert row["occurrence_count"] == 2
    assert row["first_seen"] == "2026-01-01"
    assert row["last_seen"] == "2026-02-01"
    assert row["previously_reported"] is True
    assert row["anomaly_id"] == first[0]["anomaly_id"]
