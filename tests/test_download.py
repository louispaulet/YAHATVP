"""Download-boundary validation tests for source response formats."""

from pathlib import Path

import pytest

from hatvp.download.validation import (
    is_supported_name,
    response_kind,
    source_extension,
    source_name_for_kind,
    supported_source_names,
    validate_dataset_prefix,
    validate_source_name,
)


def write_source(tmp_path: Path, name: str, content: bytes) -> Path:
    """Write a small response fixture at the validator's file boundary."""

    path = tmp_path / name
    path.write_bytes(content)
    return path


def test_xml_with_utf8_bom_is_accepted(tmp_path: Path) -> None:
    path = write_source(
        tmp_path,
        "declarations.xml",
        b'\xef\xbb\xbf<?xml version="1.0"?><declarations></declarations>',
    )

    validate_dataset_prefix(path, "declarations.xml")


def test_xml_with_leading_whitespace_is_accepted(tmp_path: Path) -> None:
    path = write_source(tmp_path, "declarations.xml", b" \n\t<declarations></declarations>")

    validate_dataset_prefix(path, "declarations.xml")


def test_csv_requires_a_semicolon_in_the_header(tmp_path: Path) -> None:
    valid = write_source(tmp_path, "liste.csv", b"id_origine;url_dossier\nA;fixture\n")
    validate_dataset_prefix(valid, "liste.csv")

    invalid = write_source(tmp_path, "invalid.csv", b"id_origine,url_dossier\nA,fixture\n")
    with pytest.raises(ValueError, match="semicolon-delimited"):
        validate_dataset_prefix(invalid, "liste.csv")


def test_empty_and_unrelated_responses_are_rejected(tmp_path: Path) -> None:
    empty = write_source(tmp_path, "empty.xml", b"")
    with pytest.raises(ValueError, match="empty"):
        validate_dataset_prefix(empty, "declarations.xml")

    html = write_source(tmp_path, "html.xml", b"<html>not the dataset</html>")
    with pytest.raises(ValueError, match="XML document"):
        validate_dataset_prefix(html, "declarations.xml")


def test_source_name_helpers_keep_the_supported_contract() -> None:
    assert supported_source_names() == ("declarations.xml", "liste.csv")
    assert response_kind("declarations.xml") == "xml"
    assert response_kind("liste.csv") == "csv"
    assert response_kind("archive.zip") == "unknown"
    assert source_extension("DECLARATIONS.XML") == ".xml"
    assert is_supported_name("liste.csv")
    assert not is_supported_name("archive.zip")
    assert source_name_for_kind("xml") == "declarations.xml"
    assert source_name_for_kind("csv") == "liste.csv"


def test_source_name_validation_rejects_unknown_kind() -> None:
    validate_source_name("declarations.xml")

    with pytest.raises(ValueError, match="Unsupported HATVP source name"):
        validate_source_name("archive.zip")

    with pytest.raises(ValueError, match="Unsupported HATVP source kind"):
        source_name_for_kind("zip")
