"""Curated BigQuery boundary and stable table allowlist."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .loader import load_parquet_tables

CURATED_TABLES = ("declarations", "people", "incomes", "assets")


def curated_table_names() -> tuple[str, ...]:
    """Return the four production tables in deterministic load order."""

    return CURATED_TABLES


def validate_table_selection(table_names: Sequence[str]) -> tuple[str, ...]:
    """Validate callers do not accidentally send non-curated tables to BQ."""

    selected = tuple(table_names)
    unsupported = [name for name in selected if name not in CURATED_TABLES]
    if unsupported:
        raise ValueError(f"Unsupported curated BigQuery tables: {', '.join(unsupported)}")
    return selected


def validate_table_files(
    table_files: dict[str, Path], table_names: Sequence[str] = CURATED_TABLES
) -> tuple[str, ...]:
    """Validate that every selected table has a local or staged Parquet file."""

    selected = validate_table_selection(table_names)
    missing = [name for name in selected if name not in table_files]
    if missing:
        raise ValueError(f"Missing required BigQuery table files: {', '.join(missing)}")
    return selected


def load_curated_tables(
    *,
    project: str,
    dataset: str,
    table_files: dict[str, Path],
    snapshot_date: str,
    gcs_uris: dict[str, str] | None = None,
    table_names: Sequence[str] = CURATED_TABLES,
    location: str = "europe-west1",
    client: Any | None = None,
) -> None:
    """Compatibility wrapper that rejects non-curated table selections."""

    load_parquet_tables(
        project=project,
        dataset=dataset,
        table_files=table_files,
        snapshot_date=snapshot_date,
        gcs_uris=gcs_uris,
        table_names=validate_table_selection(table_names),
        location=location,
        client=client,
    )


__all__ = [
    "CURATED_TABLES",
    "curated_table_names",
    "load_curated_tables",
    "load_parquet_tables",
    "validate_table_files",
    "validate_table_selection",
]
