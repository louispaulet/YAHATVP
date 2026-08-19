"""Unit tests for source-preserving text, date, and number normalization."""

import pytest

from hatvp.normalize import (
    MISSING_MARKERS,
    normalize_text,
    parse_date,
    parse_french_number,
    parse_year,
    raw_text,
)


def test_french_number_normalization() -> None:
    assert parse_french_number("50 000,00") == 50000.0
    assert parse_french_number("50\u202f000,00 €") == 50000.0
    assert parse_french_number("(1 200,50)") == -1200.5


def test_missing_values_and_dates() -> None:
    assert normalize_text(" [Données non publiées] ") is None
    assert normalize_text("  Élu   local ") == "Élu local"
    assert parse_date("01/12/2025 08:30:00") == "2025-12-01"
    assert parse_date("01/2025") == "2025-01-01"
    assert parse_year("2007") == 2007
    assert parse_year("21/05/2012") == 2012


def test_raw_text_collapses_whitespace_without_missing_marker_logic() -> None:
    assert raw_text("  Alice\n Dupont ") == "Alice Dupont"
    assert raw_text("  ") is None


def test_numeric_parser_handles_native_values_and_invalid_text() -> None:
    assert parse_french_number(12) == 12.0
    assert parse_french_number(1.5) == 1.5
    assert parse_french_number("not-a-number") is None
    assert "néant" in MISSING_MARKERS


@pytest.mark.parametrize("marker", sorted(MISSING_MARKERS))
def test_all_missing_markers_normalize_to_none(marker: str) -> None:
    assert normalize_text(marker) is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("2025-12-01", "2025-12-01"), ("2025-12", "2025-12-01"), ("bad", None)],
)
def test_date_parser_supports_iso_and_rejects_unknown_formats(
    raw: str, expected: str | None
) -> None:
    assert parse_date(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("1.234,56", 1234.56), ("1.234.567", 1234567.0), ("50%", 50.0)],
)
def test_number_parser_handles_grouping_and_suffixes(raw: str, expected: float) -> None:
    assert parse_french_number(raw) == expected


def test_normalize_text_preserves_non_marker_case_and_accents() -> None:
    assert normalize_text("Données utiles") == "Données utiles"
    assert normalize_text("NULLABLE") == "NULLABLE"


def test_normalizers_accept_missing_native_values() -> None:
    assert normalize_text(None) is None
    assert parse_date(None) is None
    assert parse_french_number(None) is None
