"""Polars Parquet writers used by local and GCS artifact stages."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl

from .table_columns import required_columns
from .table_schema import schema_for


def write_parquet(
    rows: list[dict[str, Any]],
    path: Path,
    required: list[str],
    schema: dict[str, object] | None = None,
) -> None:
    schema = schema or {}
    columns = list(dict.fromkeys([*required, *schema]))
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


def write_table(rows: list[dict[str, Any]], table_name: str, path: Path) -> None:
    """Write a named table using its shared column and type contracts."""

    write_parquet(rows, path, required_columns(table_name), schema_for(table_name))


__all__ = ["write_parquet", "write_table"]
