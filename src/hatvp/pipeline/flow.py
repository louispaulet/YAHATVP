"""Pure Bronze-to-Silver-to-Gold build flow used by the pipeline runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..layers import build_gold, build_silver
from ..layers.silver import apply_registry_states
from ..storage import ArtifactStore
from .layers import write_bronze_tables, write_gold_tables, write_silver_tables
from .registry_artifacts import write_registry


def build_layers(
    store: ArtifactStore,
    tables: dict[str, list[dict[str, Any]]],
    history: dict[str, list[dict[str, Any]]],
    registry: list[dict[str, Any]],
    snapshot: str,
    work: Path,
    dry_run: bool,
    dob_max_age_years: int | None = None,
) -> dict[str, Path]:
    """Build and persist all analytical layer files before state advancement."""

    silver, silver_history, registry_rows = build_silver(
        tables,
        history,
        registry,
        snapshot_date=snapshot,
        dob_max_age_years=dob_max_age_years,
    )
    gold, registry_rows = build_gold(silver_history, registry_rows)
    silver = apply_registry_states(silver, registry_rows)
    gold = apply_registry_states(gold, registry_rows)
    files = write_bronze_tables(store, tables, snapshot, work, dry_run)
    files.update(write_silver_tables(store, silver, snapshot, work, dry_run))
    files.update(write_gold_tables(store, gold, snapshot, work, dry_run))
    files.update(write_registry(store, registry_rows, snapshot, work, dry_run))
    return files


def layer_file_contract() -> tuple[str, ...]:
    """Describe the physical files required before BigQuery loading."""

    return (
        "declarations",
        "people",
        "incomes",
        "assets",
        "silver_declarations",
        "silver_people",
        "silver_incomes",
        "silver_assets",
        "gold_declarations",
        "gold_people",
        "gold_incomes",
        "gold_assets",
        "anomaly_registry",
    )


def layer_object_prefix(layer: str) -> str:
    """Return a validated logical prefix for one derived artifact layer."""

    if layer not in {"bronze", "silver", "gold", "anomaly_registry"}:
        raise ValueError(f"Unknown analytical layer: {layer}")
    return f"{layer}/"


def layer_table_aliases() -> dict[str, str]:
    """Map physical derived tables to their logical object layers."""

    return (
        {name: "silver" for name in layer_file_contract()[4:8]}
        | {name: "gold" for name in layer_file_contract()[8:12]}
        | {"anomaly_registry": "anomaly_registry"}
    )


__all__ = ["build_layers", "layer_file_contract"]
