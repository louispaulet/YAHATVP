"""Artifact writers for explicit Bronze, Silver, Gold, and registry layers."""

from __future__ import annotations

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
        path = work / f"{layer}_{source_name}.parquet"
        if bronze:
            write_table(tables.get(name, []), source_name, path)
        else:
            schema = {**schema_for(source_name), **SILVER_FIELDS}
            write_parquet(
                tables.get(source_name, []),
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
        # Layer dictionaries are large Python object graphs. Each table has
        # already been serialized, so release its rows before writing the next.
        tables.pop(source_name, None)
    return files


__all__ = ["write_bronze_tables", "write_gold_tables", "write_silver_tables"]
