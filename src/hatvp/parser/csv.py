"""Semicolon-delimited HATVP listing parser."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from ..config import load_pipeline_config
from ..models import ParseContext
from ..normalize import normalize_text

CSV_SOURCE_FILE = "liste.csv"


def parse_csv(path: Path, snapshot_date: str) -> list[dict[str, Any]]:
    """Parse the listing while retaining all source columns and values."""

    config = load_pipeline_config().parser
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter=config.csv_delimiter)
        if not reader.fieldnames:
            raise ValueError("HATVP CSV has no header")
        validate_identity_columns(reader.fieldnames, config.csv_identity_columns)
        return [_row(row, ParseContext(snapshot_date, CSV_SOURCE_FILE)) for row in reader]


def _row(row: dict[str, str | None], context: ParseContext) -> dict[str, Any]:
    values = {key: normalize_text(value) for key, value in row.items() if key is not None}
    values.update({"snapshot_date": context.snapshot_date, "source_file": context.source_file})
    return values


def validate_identity_columns(fieldnames: list[str], candidates: tuple[str, ...]) -> None:
    """Require at least one configured source identity column in the listing."""

    if not any(name in fieldnames for name in candidates):
        raise ValueError("HATVP CSV is missing expected identity columns")


def csv_config() -> tuple[str, tuple[str, ...]]:
    """Expose delimiter and identity candidates for fixture-backed tests."""

    config = load_pipeline_config().parser
    return config.csv_delimiter, config.csv_identity_columns


def csv_row_count(path: Path) -> int:
    """Count listing data rows without normalizing or mutating source bytes."""

    with path.open("r", encoding="utf-8-sig", newline="") as source:
        return max(sum(1 for _ in source) - 1, 0)


def csv_has_header(path: Path) -> bool:
    """Return whether a listing has a non-empty header row."""

    with path.open("r", encoding="utf-8-sig", newline="") as source:
        return bool(source.readline().strip())


def csv_delimiter() -> str:
    """Return the configured delimiter for callers building compatible fixtures."""

    return csv_config()[0]


__all__ = [
    "csv_config",
    "csv_delimiter",
    "csv_has_header",
    "csv_row_count",
    "CSV_SOURCE_FILE",
    "parse_csv",
    "validate_identity_columns",
]
