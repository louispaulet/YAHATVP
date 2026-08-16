from pathlib import Path

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
    assert tables["assets"][0]["normalized_value"] == 12345.67
    assert tables["participations"][0]["evaluation_eur"] == 1200.5
    assert len(tables["liste"]) == 2


def test_single_real_declaration_fixture_is_the_first_acceptance_case() -> None:
    tables = parse_xml(FIXTURES / "declaration_single_real.xml", "2026-08-16")

    assert len(tables["declarations"]) == 1
    assert tables["declarations"][0]["declaration_uuid"] == ("40c65083-094f-4170-9e21-b9c95f4390d6")
    assert tables["people"][0]["nom"] == "ABAD"
    assert len(tables["mandates"]) >= 6
    assert len(tables["participations"]) >= 2
