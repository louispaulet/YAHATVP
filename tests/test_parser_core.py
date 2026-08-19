"""Acceptance tests for the public parser façade and observed fixture schema."""

import json

from hatvp.parser import parser_config, parser_source_tables, parser_table_names
from tests.parser_support import csv_rows, has_provenance, nonempty_tables, xml_tables


def test_parser_uses_observed_xml_structure() -> None:
    tables = xml_tables()

    assert len(tables["declarations"]) == 2
    assert tables["declarations"][0]["declaration_uuid"] == "fixture-uuid-1"
    assert tables["declarations"][0]["mandat_label"] == "Élu local"
    assert tables["people"][0]["email"] is None
    assert tables["incomes"][0]["normalized_value"] == 12000.0
    mandate_income = tables["incomes"][1]
    assert mandate_income["income_stream"] == "mandate_remuneration"
    assert mandate_income["income_year"] == "2025"
    assert mandate_income["income_type"] == "Maire"
    assert mandate_income["normalized_value"] == 50000.0
    assert tables["mandate_remunerations"][0]["description"] == "Maire"
    assert tables["mandate_remunerations"][0]["remuneration_year"] == 2025
    assert tables["assets"][0]["normalized_value"] == 12345.67
    assert tables["participations"][0]["evaluation_eur"] == 1200.5
    assert len(csv_rows()) == 2


def test_parser_public_table_and_configuration_boundaries_are_stable() -> None:
    names = parser_table_names()
    config = parser_config()

    assert names == parser_source_tables()
    assert "declarations" in names
    assert "people" in names
    assert config.xml_root == "declarations"
    assert config.csv_delimiter == ";"
    assert config.section("income") == "revenuMandatDto"
    assert config.candidates("asset_value")


def test_listing_rows_keep_source_file_and_snapshot_provenance() -> None:
    rows = csv_rows()

    assert all(row["snapshot_date"] == "2026-08-16" for row in rows)
    assert all(row["source_file"] == "liste.csv" for row in rows)
    assert rows[0]["id_origine"] == "SOURCE-1"


def test_parser_table_lengths_remain_nonempty_for_fixture_sections() -> None:
    tables = xml_tables()

    assert len(tables["declarations"]) == 2
    assert len(tables["people"]) == 2
    assert len(tables["mandates"]) >= 2
    assert len(tables["activities"]) == 0
    assert len(tables["participations"]) >= 1


def test_core_rows_retain_snapshot_and_source_provenance() -> None:
    tables = xml_tables()

    assert has_provenance(tables["declarations"][0])
    assert tables["declarations"][0]["snapshot_date"] == "2026-08-16"
    assert tables["declarations"][0]["source_file"] == "declarations.xml"
    assert "declarations" in nonempty_tables(tables)


def test_people_rows_keep_public_identity_fields_even_when_optional() -> None:
    row = xml_tables()["people"][0]

    assert row["declaration_uuid"] == "fixture-uuid-1"
    assert row["prenom"] == "Alice"
    assert row["nom"] == "DUPONT"
    assert "email" in row
    assert row["date_naissance"] == "1980-03-02"
    assert row["date_naissance_year"] == 1980
    assert str(row["date_naissance_date"]) == "1980-03-02"


def test_bronze_keeps_amended_occurrences_and_source_evidence() -> None:
    declarations = xml_tables("versioned_declarations.xml")["declarations"]

    assert len(declarations) == 2
    assert {row["declaration_uuid"] for row in declarations} == {"versioned-declaration"}
    assert len({row["bronze_record_key"] for row in declarations}) == 2
    assert {row["declaration_modificative"] for row in declarations} == {"false", "true"}
    assert all(row["source_snapshot_date"] == "2026-08-16" for row in declarations)
    assert json.loads(declarations[0]["raw_record_json"])["uuid"] == "versioned-declaration"


def test_parser_metadata_links_rows_to_immutable_raw_source() -> None:
    row = xml_tables()["declarations"][0]
    assert row["source_format"] == "xml"
    assert row["source_object"].endswith("declarations.xml")
    assert row["parser_version"] == "2"
