"""Fixture tests for declared-income and unified mandate-income components."""

import json

from hatvp.parser_income import income_row_count
from hatvp.parser_income_fields import (
    income_has_numeric_value,
    income_numeric_pair,
    income_value_pair,
)
from hatvp.parser_mandate_income import is_mandate_income_row, mandate_income_years
from tests.parser_support import first_row, raw_record, rows_for, xml_tables


def test_single_real_declaration_preserves_annual_remunerations() -> None:
    tables = xml_tables("declaration_single_real.xml")
    uuid = "40c65083-094f-4170-9e21-b9c95f4390d6"
    remuneration_rows = [
        row
        for row in rows_for(tables, "mandate_remunerations", uuid)
        if row["source_item_index"] == 0
    ]

    assert len(tables["mandates"]) >= 6
    assert [row["remuneration_year"] for row in remuneration_rows] == [
        2019,
        2020,
        2021,
        2022,
        2023,
        2024,
    ]
    assert [row["normalized_value"] for row in remuneration_rows] == [
        71105.0,
        70773.0,
        70676.0,
        63050.0,
        73698.0,
        43491.0,
    ]
    assert len(tables["participations"]) >= 2


def test_unified_income_keeps_zero_annual_remunerations() -> None:
    tables = xml_tables("declaration_single_real.xml")
    rows = [
        row
        for row in tables["incomes"]
        if is_mandate_income_row(row) and row["source_item_index"] == 2
    ]

    assert len(rows) == 4
    assert [row["normalized_value"] for row in rows] == [0.0, 0.0, 0.0, 0.0]
    assert mandate_income_years(rows) == ["2019", "2020", "2021", "2022"]


def test_income_slots_exclude_empty_categories_and_use_total_fallback() -> None:
    tables = xml_tables("income_slots.xml")

    assert len(tables["incomes"]) == 2
    assert [row["income_type"] for row in tables["incomes"]] == [
        "Traitements, salaires",
        "totalElu",
    ]
    assert [row["normalized_value"] for row in tables["incomes"]] == [10000.0, 12000.0]
    assert income_row_count(tables["incomes"]) == 2


def test_income_field_helpers_read_both_declared_values() -> None:
    row = first_row(xml_tables(), "incomes", income_stream="revenu_mandat")

    assert income_value_pair(row)[0] == "12 000,00"
    assert income_numeric_pair(row) == (12000.0, None)
    assert income_has_numeric_value(row)
    assert json.loads(row["raw_record_json"])["revenuElu"] == "12 000,00"


def test_mandate_rows_retain_all_annual_raw_source_values() -> None:
    tables = xml_tables("declaration_single_real.xml")
    mandate = first_row(tables, "mandates", source_item_index=0, source_section="mandatElectifDto")
    record = raw_record(mandate)

    assert mandate["remuneration_raw"] is None
    assert mandate["remuneration_count"] == 6
    assert record["remuneration"]["amounts"][-1] == {"annee": "2024", "montant": "43 491"}
