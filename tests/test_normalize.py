from hatvp.normalize import normalize_text, parse_date, parse_french_number


def test_french_number_normalization() -> None:
    assert parse_french_number("50 000,00") == 50000.0
    assert parse_french_number("50\u202f000,00 €") == 50000.0
    assert parse_french_number("(1 200,50)") == -1200.5


def test_missing_values_and_dates() -> None:
    assert normalize_text(" [Données non publiées] ") is None
    assert normalize_text("  Élu   local ") == "Élu local"
    assert parse_date("01/12/2025 08:30:00") == "2025-12-01"
    assert parse_date("01/2025") == "2025-01-01"
