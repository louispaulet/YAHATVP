"""Fixture tests for asset and liability DTO components."""

from hatvp.parser_finance import asset_rows, liability_rows
from hatvp.xml_support import local_name
from tests.parser_support import asset_sections, first_row, xml_tables


def test_parser_covers_observed_asset_and_liability_dtos() -> None:
    tables = xml_tables("asset_sections.xml")

    assert asset_sections(tables) == {
        "immeubleDto",
        "sciDto",
        "valeursNonEnBourseDto",
        "valeursEnBourseDto",
        "assuranceVieDto",
        "comptesBancaireDto",
        "bienDiverDto",
        "vehiculeDto",
        "fondDto",
        "autreBienDto",
        "bienEtrangerDto",
    }
    assert len(tables["assets"]) == 11
    assert tables["assets"][0]["normalized_value"] == 250000.0
    assert tables["liabilities"][0]["normalized_value"] == 10000.0


def test_finance_rows_preserve_source_positions_and_values() -> None:
    tables = xml_tables("asset_sections.xml")
    asset = tables["assets"][0]
    liability = tables["liabilities"][0]

    assert asset["source_section"] == "immeubleDto"
    assert asset["source_item_index"] == 0
    assert asset["raw_value"] == "250 000,00"
    assert liability["source_section"] == "passifDto"
    assert liability["raw_value"] == "10 000,00"


def test_finance_component_exports_are_callable() -> None:
    tables = xml_tables()
    declaration = next(row for row in tables["declarations"] if row["declaration_uuid"])

    assert declaration["declaration_uuid"] == "fixture-uuid-1"
    assert callable(asset_rows)
    assert callable(liability_rows)
    assert local_name("{urn:test}asset") == "asset"


def test_first_asset_has_the_expected_normalized_contract() -> None:
    row = first_row(xml_tables("asset_sections.xml"), "assets", source_item_index=0)

    assert row["declaration_uuid"] == "fixture-assets-1"
    assert row["snapshot_date"] == "2026-08-16"
    assert row["quality_status"] == "OK"
    assert row["quality_reason"] is None


def test_finance_rows_have_explicit_source_identity_fields() -> None:
    tables = xml_tables("asset_sections.xml")
    assets = tables["assets"]

    assert all(row["declaration_uuid"] == "fixture-assets-1" for row in assets)
    assert [row["source_item_index"] for row in assets[:3]] == [0, 0, 0]
    assert all(row["snapshot_date"] == "2026-08-16" for row in assets)


def test_liability_rows_keep_numeric_values_as_normalized_floats() -> None:
    row = xml_tables("asset_sections.xml")["liabilities"][0]

    assert isinstance(row["normalized_value"], float)
    assert row["normalized_value"] == 10000.0
