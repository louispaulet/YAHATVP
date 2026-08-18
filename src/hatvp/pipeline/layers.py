"""Artifact writers for explicit Bronze, Silver, Gold, and registry layers."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from ..layers import GOLD_TABLES, SILVER_TABLES
from ..layers.silver import SILVER_FIELDS
from ..storage import ArtifactStore
from ..tables import write_parquet, write_table
from ..tables.columns import required_columns
from ..tables.schema import schema_for


def write_bronze_tables(
    store: ArtifactStore,
    tables: dict[str, list[dict[str, Any]]],
    snapshot: str,
    work: Path,
    dry_run: bool,
) -> dict[str, Path]:
    """Write source-shaped parser output and return local files for loading."""

    return _write_layer(store, tables, "bronze", snapshot, work, dry_run, bronze=True)


def write_silver_tables(
    store: ArtifactStore,
    tables: dict[str, list[dict[str, Any]]],
    snapshot: str,
    work: Path,
    dry_run: bool,
) -> dict[str, Path]:
    """Write anomaly-annotated current partitions under Silver."""

    return _write_layer(store, tables, "silver", snapshot, work, dry_run, names=SILVER_TABLES)


def write_gold_tables(
    store: ArtifactStore,
    tables: dict[str, list[dict[str, Any]]],
    snapshot: str,
    work: Path,
    dry_run: bool,
) -> dict[str, Path]:
    """Write latest-declarant rows under Gold with physical table aliases."""

    return _write_layer(store, tables, "gold", snapshot, work, dry_run, names=GOLD_TABLES)


def _write_layer(
    store: ArtifactStore,
    tables: dict[str, list[dict[str, Any]]],
    layer: str,
    snapshot: str,
    work: Path,
    dry_run: bool,
    *,
    bronze: bool = False,
    names: tuple[str, ...] = (),
) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for name in names or tuple(tables):
        source_name = name.removeprefix("silver_").removeprefix("gold_")
        path_name = source_name if bronze else name
        path = work / f"{path_name}.parquet"
        if bronze:
            write_table(_serializable_rows(tables.get(name, [])), source_name, path)
        else:
            schema = {**schema_for(source_name), **SILVER_FIELDS}
            write_parquet(
                _serializable_rows(tables.get(source_name, [])),
                path,
                required_columns(source_name),
                schema,
            )
        files[path_name if bronze else f"{layer}_{source_name}"] = path
        if not dry_run:
            store.put_file(
                f"{layer}/{source_name}/snapshot_date={snapshot}/data.parquet",
                path,
                content_type="application/vnd.apache.parquet",
            )
    return files


def _serializable_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: _serializable(value) for key, value in row.items()} for row in rows]


def _serializable(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


__all__ = ["write_bronze_tables", "write_gold_tables", "write_silver_tables"]
