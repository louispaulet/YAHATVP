"""Semicolon-delimited HATVP listing parser."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .config import load_pipeline_config
from .models import ParseContext
from .normalize import normalize_text


def parse_csv(path: Path, snapshot_date: str) -> list[dict[str, Any]]:
    """Parse the listing while retaining all source columns and values."""

    config = load_pipeline_config().parser
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter=config.csv_delimiter)
        if not reader.fieldnames:
            raise ValueError("HATVP CSV has no header")
        if not any(name in reader.fieldnames for name in config.csv_identity_columns):
            raise ValueError("HATVP CSV is missing expected identity columns")
        return [_row(row, ParseContext(snapshot_date, "liste.csv")) for row in reader]


def _row(row: dict[str, str | None], context: ParseContext) -> dict[str, Any]:
    values = {key: normalize_text(value) for key, value in row.items() if key is not None}
    values.update({"snapshot_date": context.snapshot_date, "source_file": context.source_file})
    return values


__all__ = ["parse_csv"]
