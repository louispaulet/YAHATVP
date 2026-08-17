"""Polars Parquet writers used by local and GCS artifact stages."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl

from .columns import required_columns
from .schema import schema_for


def write_parquet(
    rows: list[dict[str, Any]],
    path: Path,
    required: list[str],
    schema: dict[str, object] | None = None,
) -> None:
    schema = schema or {}
    columns = normalized_columns(required, schema)
    frame = _frame(rows, columns, schema)
    for column in columns:
        if column not in frame.columns:
            frame = frame.with_columns(
                pl.Series(column, [None] * frame.height, dtype=schema.get(column, pl.Null))
            )
    for column, dtype in schema.items():
        expression = pl.col(column)
        if column == "snapshot_date" and frame.schema[column] == pl.String:
            expression = expression.str.to_date(format="%Y-%m-%d", strict=True)
        frame = frame.with_columns(expression.cast(dtype, strict=True).alias(column))
    frame.write_parquet(path, compression="zstd")


def _frame(
    rows: list[dict[str, Any]], columns: list[str], schema: dict[str, object]
) -> pl.DataFrame:
    if rows:
        return pl.DataFrame(rows, infer_schema_length=None)
    return pl.DataFrame(
        {column: pl.Series(column, [], dtype=schema.get(column, pl.Null)) for column in columns}
    )


def normalized_columns(required: list[str], schema: dict[str, object]) -> list[str]:
    """Combine required and schema-only columns while preserving contract order."""

    return list(dict.fromkeys([*required, *schema]))


def parquet_schema(table_name: str) -> dict[str, object]:
    """Return a copy of the shared schema for callers preparing a fixture."""

    return dict(schema_for(table_name))


def parquet_path(directory: Path, table_name: str) -> Path:
    """Return the conventional artifact filename for one normalized table."""

    return directory / f"{table_name}.parquet"


def write_table(rows: list[dict[str, Any]], table_name: str, path: Path) -> None:
    """Write a named table using its shared column and type contracts."""

    write_parquet(rows, path, required_columns(table_name), schema_for(table_name))


__all__ = [
    "normalized_columns",
    "parquet_path",
    "parquet_schema",
    "write_parquet",
    "write_table",
]
