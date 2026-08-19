"""Unit coverage for explicit Gold DOB quality metadata."""

from __future__ import annotations

from typing import Any

import pytest

from hatvp.layers.dob_quality import (
    QUALITY_STATUSES,
    is_review_status,
    quality_fields,
    reason_for,
    status_for,
)
from hatvp.layers.gold import build_gold
from hatvp.layers.silver import build_silver
from hatvp.normalize import parse_date
from tests.layers_support import declaration, people


def person_row(value: str | None) -> dict[str, Any]:
    """Build the smallest source-shaped people row for quality tests."""

    return {
        **people("dob-quality", "2026-01-01", value or ""),
        "date_naissance_raw": value,
        "date_naissance": parse_date(value),
    }


def rule(rule_id: str) -> dict[str, Any]:
    """Build one anomaly rule occurrence with its stable ID."""

    return {"rule_id": rule_id}


@pytest.mark.parametrize(
    ("value", "items", "expected"),
    [
        ("1980-01-01", [], "valid"),
        (None, [], "missing"),
        ("not-a-date", [], "invalid"),
        ("1925-01-01", [rule("PERSON_DOB_IMPLAUSIBLE")], "implausible"),
        ("1980-01-01", [rule("PERSON_DOB_CONFLICT")], "conflicting"),
        (
            "1925-01-01",
            [rule("PERSON_DOB_IMPLAUSIBLE"), rule("PERSON_DOB_CONFLICT")],
            "implausible_conflicting",
        ),
    ],
)
def test_status_for_keeps_missing_invalid_and_anomaly_states_distinct(
    value: str | None, items: list[dict[str, Any]], expected: str
) -> None:
    assert status_for(person_row(value), items) == expected
    assert quality_fields(person_row(value), items)["date_naissance_quality_status"] == expected


def test_quality_fields_explain_invalid_source_values() -> None:
    fields = quality_fields(person_row("not-a-date"), [])

    assert fields["date_naissance_quality_reason"] == "unparseable source value"


def test_quality_reason_is_stable_and_only_contains_dob_rules() -> None:
    items = [rule("OTHER"), rule("PERSON_DOB_CONFLICT"), rule("PERSON_DOB_IMPLAUSIBLE")]

    assert reason_for(items) == "PERSON_DOB_CONFLICT, PERSON_DOB_IMPLAUSIBLE"


def test_review_status_inventory_is_explicit() -> None:
    assert QUALITY_STATUSES == (
        "valid",
        "missing",
        "invalid",
        "implausible",
        "conflicting",
        "implausible_conflicting",
    )
    assert is_review_status("implausible")
    assert not is_review_status("valid")


def test_gold_keeps_the_observed_date_and_exposes_quality_fields() -> None:
    tables = {
        "declarations": [declaration("dob-quality", "2026-01-01", "2026-01-01")],
        "people": [person_row("1925-01-01")],
        "incomes": [],
        "assets": [],
    }
    _, history, registry = build_silver(tables, {}, snapshot_date="2026-01-01")
    gold, _ = build_gold(history, registry)

    assert gold["people"][0]["date_naissance"] == "1925-01-01"
    assert gold["people"][0]["date_naissance_quality_status"] == "implausible"
