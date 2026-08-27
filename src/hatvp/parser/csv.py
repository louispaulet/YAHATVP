"""Semicolon-delimited HATVP listing parser."""

from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ..config import load_pipeline_config
from ..models import ParseContext
from ..normalize import normalize_text
from ..xml_support import raw_record
from .provenance import apply_provenance, context_for, record_key

CSV_SOURCE_FILE = "liste.csv"


def parse_csv(
    path: Path, snapshot_date: str, source_metadata: Mapping[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Parse the listing while retaining all source columns and values."""

    config = load_pipeline_config().parser
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter=config.csv_delimiter)
        if not reader.fieldnames:
            raise ValueError("HATVP CSV has no header")
        validate_identity_columns(reader.fieldnames, config.csv_identity_columns)
        context = context_for(snapshot_date, CSV_SOURCE_FILE, "csv", str(path), source_metadata)
        return [
            _row(row, context, index, config.csv_identity_columns)
            for index, row in enumerate(reader)
        ]


def _row(
    row: dict[str, str | None], context: ParseContext, index: int, identity_columns: tuple[str, ...]
) -> dict[str, Any]:
    source_id = next(
        (
            value
            for name in identity_columns
            if (value := normalize_text(row.get(name))) is not None
        ),
        None,
    )
    values = {key: normalize_text(value) for key, value in row.items() if key is not None}
    values.update({"snapshot_date": context.snapshot_date, "raw_record_json": raw_record(row)})
    return apply_provenance(
        values,
        context,
        record_key(context, source_id, index),
        source_id,
        f"{context.source_file}#/row[{index}]",
    )


def validate_identity_columns(fieldnames: list[str], candidates: tuple[str, ...]) -> None:
    if not any(name in fieldnames for name in candidates):
        raise ValueError("HATVP CSV is missing expected identity columns")


def csv_config() -> tuple[str, tuple[str, ...]]:
    config = load_pipeline_config().parser
    return config.csv_delimiter, config.csv_identity_columns


def csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        return max(sum(1 for _ in source) - 1, 0)


def csv_has_header(path: Path) -> bool:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        return bool(source.readline().strip())


def csv_delimiter() -> str:
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
