"""Lightweight response validation before a source file is published."""

from __future__ import annotations

from pathlib import Path


def validate_dataset_prefix(path: Path, name: str) -> None:
    """Reject empty or clearly unrelated responses without parsing the dataset."""

    with path.open("rb") as source:
        prefix = source.read(4096).lstrip().lower()
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


__all__ = ["response_kind", "validate_dataset_prefix"]
