"""Lightweight response validation before a source file is published."""

from __future__ import annotations

from pathlib import Path


def validate_dataset_prefix(path: Path, name: str) -> None:
    """Reject empty or clearly unrelated responses without parsing the dataset."""

    with path.open("rb") as source:
        prefix = source.read(4096).removeprefix(b"\xef\xbb\xbf").lstrip().lower()
    if not prefix:
        raise ValueError(f"Downloaded {name} is empty")
    if name.endswith(".xml") and not (
        prefix.startswith(b"<?xml") or prefix.startswith(b"<declarations")
    ):
        raise ValueError(f"Downloaded {name} does not look like an XML document")
    if name.endswith(".csv") and b";" not in prefix.splitlines()[0]:
        raise ValueError(f"Downloaded {name} does not look like a semicolon-delimited CSV")


def response_kind(name: str) -> str:
    """Return the supported source kind used in structured download logs."""

    if name.endswith(".xml"):
        return "xml"
    if name.endswith(".csv"):
        return "csv"
    return "unknown"


def is_supported_name(name: str) -> bool:
    """Return whether a downloaded source has a validator in this module."""

    return response_kind(name) != "unknown"


def validate_source_name(name: str) -> None:
    """Reject unsupported source names before network bytes are published."""

    if not is_supported_name(name):
        raise ValueError(f"Unsupported HATVP source name: {name}")


def supported_source_names() -> tuple[str, ...]:
    """Return the source names accepted by the downloader boundary."""

    return ("declarations.xml", "liste.csv")


def source_extension(name: str) -> str:
    """Return the lowercase extension used by response validation."""

    return Path(name).suffix.casefold()


def source_name_for_kind(kind: str) -> str:
    """Return the canonical source filename for a supported response kind."""

    names = {"xml": "declarations.xml", "csv": "liste.csv"}
    try:
        return names[kind]
    except KeyError as exc:
        raise ValueError(f"Unsupported HATVP source kind: {kind}") from exc


__all__ = [
    "is_supported_name",
    "response_kind",
    "source_extension",
    "supported_source_names",
    "validate_dataset_prefix",
    "validate_source_name",
]
