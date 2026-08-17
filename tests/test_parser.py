import json
from pathlib import Path

import pytest

from hatvp.parser import parse_sources, parse_xml

FIXTURES = Path(__file__).parent / "fixtures"


def test_parser_uses_observed_xml_structure() -> None:
    tables = parse_sources(
        FIXTURES / "liste.csv",
        FIXTURES / "declarations.xml",
        "2026-08-16",
    )

    assert len(tables["declarations"]) == 2
    assert tables["declarations"][0]["declaration_uuid"] == "fixture-uuid-1"
    assert tables["declarations"][0]["mandat_label"] == "Élu local"
    assert tables["people"][0]["email"] is None
    assert tables["incomes"][0]["normalized_value"] == 12000.0
    mandate_remuneration = tables["mandate_remunerations"][0]
    assert mandate_remuneration["description"] == "Maire"
    assert mandate_remuneration["remuneration_year"] == 2025
    assert mandate_remuneration["normalized_value"] == 50000.0
    assert tables["assets"][0]["normalized_value"] == 12345.67
    assert tables["participations"][0]["evaluation_eur"] == 1200.5
    assert len(tables["liste"]) == 2


def test_single_real_declaration_fixture_is_the_first_acceptance_case() -> None:
    tables = parse_xml(FIXTURES / "declaration_single_real.xml", "2026-08-16")

    assert len(tables["declarations"]) == 1
    assert tables["declarations"][0]["declaration_uuid"] == ("40c65083-094f-4170-9e21-b9c95f4390d6")
    assert tables["people"][0]["nom"] == "ABAD"
    assert len(tables["mandates"]) >= 6
    remuneration_rows = [
        row
        for row in tables["mandate_remunerations"]
        if row["declaration_uuid"] == "40c65083-094f-4170-9e21-b9c95f4390d6"
        and row["source_item_index"] == 0
    ]
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
    zero_remuneration_rows = [
        row
        for row in tables["mandate_remunerations"]
        if row["declaration_uuid"] == "40c65083-094f-4170-9e21-b9c95f4390d6"
        and row["source_item_index"] == 2
    ]
    assert [row["normalized_value"] for row in zero_remuneration_rows] == [
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    mandate_item = next(
        row
        for row in tables["mandates"]
        if row["declaration_uuid"] == "40c65083-094f-4170-9e21-b9c95f4390d6"
        and row["source_section"] == "mandatElectifDto"
        and row["source_item_index"] == 0
    )
    assert mandate_item["remuneration_raw"] is None
    assert mandate_item["remuneration_count"] == 6
    raw_record = json.loads(mandate_item["raw_record_json"])
    assert raw_record["remuneration"]["amounts"][-1] == {
        "annee": "2024",
        "montant": "43 491",
    }
    assert len(tables["participations"]) >= 2


def test_parser_covers_observed_asset_and_liability_dtos() -> None:
    tables = parse_xml(FIXTURES / "asset_sections.xml", "2026-08-16")

    asset_sections = {row["source_section"] for row in tables["assets"]}
    assert asset_sections == {
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


def test_parser_handles_empty_optional_declaration_sections() -> None:
    tables = parse_xml(FIXTURES / "edge_case_declarations.xml", "2026-08-16")

    by_declaration = {
        declaration["declaration_uuid"]: declaration for declaration in tables["declarations"]
    }
    assert set(by_declaration) == {
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

    missing_general_person = next(
        row for row in tables["people"] if row["declaration_uuid"] == "fixture-no-general"
    )
    assert missing_general_person["nom"] is None
    assert missing_general_person["prenom"] is None


def test_parser_excludes_empty_income_slots_and_uses_total_fallback() -> None:
    tables = parse_xml(FIXTURES / "income_slots.xml", "2026-08-16")

    assert len(tables["incomes"]) == 2
    assert [row["income_type"] for row in tables["incomes"]] == [
        "Traitements, salaires",
        "totalElu",
    ]
    assert [row["normalized_value"] for row in tables["incomes"]] == [10000.0, 12000.0]

    by_uuid = {row["declaration_uuid"]: row for row in tables["declarations"]}
    assert by_uuid["fixture-income-slots"]["income_section_present"] is True
    assert by_uuid["fixture-income-slots"]["income_section_populated_item_count"] == 2
    assert by_uuid["fixture-empty-income-section"]["income_section_present"] is True
    assert by_uuid["fixture-empty-income-section"]["income_section_populated_item_count"] == 0


def test_parser_rejects_invalid_top_level_structure_before_normalization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "hatvp.parser._declaration_row",
        lambda *_args: pytest.fail("invalid XML was normalized"),
    )

    with pytest.raises(ValueError, match="unexpected root element"):
        parse_xml(FIXTURES / "invalid_top_level.xml", "2026-08-16")


def test_parser_rejects_invalid_top_level_child_before_normalization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "hatvp.parser._declaration_row",
        lambda *_args: pytest.fail("invalid XML was normalized"),
    )

    with pytest.raises(ValueError, match="invalid top-level element"):
        parse_xml(FIXTURES / "invalid_top_level_child.xml", "2026-08-16")
