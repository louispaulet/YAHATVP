"""Structural validation and optional-section parser tests."""

import pytest

from hatvp.parser import parse_xml
from hatvp.parser_declaration_support import (
    declaration_child_names,
    declaration_has_general,
    declaration_has_income,
    income_category_names,
)
from tests.parser_support import FIXTURES, declaration_ids, xml_tables


def test_parser_handles_empty_optional_declaration_sections() -> None:
    tables = xml_tables("edge_case_declarations.xml")

    assert declaration_ids(tables) == {
        "fixture-no-assets",
        "fixture-no-income",
        "fixture-no-mandate",
        "fixture-no-general",
    }
    assert not [row for row in tables["assets"] if row["declaration_uuid"] == "fixture-no-assets"]
    assert not [
        row for row in tables["liabilities"] if row["declaration_uuid"] == "fixture-no-assets"
    ]
    assert not [row for row in tables["incomes"] if row["declaration_uuid"] == "fixture-no-income"]
    assert not [
        row for row in tables["mandates"] if row["declaration_uuid"] == "fixture-no-mandate"
    ]
    missing_general = next(
        row for row in tables["people"] if row["declaration_uuid"] == "fixture-no-general"
    )
    assert missing_general["nom"] is None
    assert missing_general["prenom"] is None


def test_invalid_top_level_structure_is_rejected_before_normalization() -> None:
    with pytest.raises(ValueError, match="unexpected root element"):
        parse_xml(FIXTURES / "invalid_top_level.xml", "2026-08-16")


def test_invalid_top_level_child_is_rejected_before_normalization() -> None:
    with pytest.raises(ValueError, match="invalid top-level element"):
        parse_xml(FIXTURES / "invalid_top_level_child.xml", "2026-08-16")


def test_structural_component_helpers_use_namespace_safe_names() -> None:
    tables = xml_tables()
    assert declaration_has_general.__name__ == "declaration_has_general"
    assert declaration_has_income.__name__ == "declaration_has_income"
    assert tables["declarations"]
    assert isinstance(declaration_child_names, object)
    assert isinstance(income_category_names, object)


def test_optional_income_sections_report_presence_and_population_counts() -> None:
    tables = xml_tables("income_slots.xml")
    by_uuid = {row["declaration_uuid"]: row for row in tables["declarations"]}

    assert by_uuid["fixture-income-slots"]["income_section_present"] is True
    assert by_uuid["fixture-income-slots"]["income_section_populated_item_count"] == 2
    assert by_uuid["fixture-empty-income-section"]["income_section_present"] is True
    assert by_uuid["fixture-empty-income-section"]["income_section_populated_item_count"] == 0


def test_real_declaration_person_parser_preserves_missing_optional_identity() -> None:
    tables = xml_tables("edge_case_declarations.xml")

    row = next(row for row in tables["people"] if row["declaration_uuid"] == "fixture-no-general")
    assert row["nom"] is None
    assert row["prenom"] is None
    assert row["snapshot_date"] == "2026-08-16"
