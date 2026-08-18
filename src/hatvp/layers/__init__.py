"""Bronze-to-Silver-to-Gold analytical layer façade."""

from __future__ import annotations

from .gold import GOLD_TABLES, build_gold, latest_declaration_keys
from .history import load_bronze_history, load_registry
from .registry import upsert_registry
from .registry_schema import registry_schema
from .silver import SILVER_TABLES, build_silver

REGISTRY_TABLE = "anomaly_registry"
LAYER_TABLES = (*SILVER_TABLES, *GOLD_TABLES, REGISTRY_TABLE)


def silver_table_name(name: str) -> str:
    """Return the physical BigQuery name for one Silver source table."""

    return f"silver_{name}"


def gold_table_name(name: str) -> str:
    """Return the physical BigQuery name for one Gold source table."""

    return f"gold_{name}"


def layer_table_names() -> tuple[str, ...]:
    """Return derived table names in deterministic load order."""

    return LAYER_TABLES


def source_table_from_layer(name: str) -> str:
    """Map a physical derived table back to its normalized source table."""

    for prefix in ("silver_", "gold_"):
        if name.startswith(prefix):
            return name.removeprefix(prefix)
    raise ValueError(f"Unknown derived table: {name}")


def is_layer_table(name: str) -> bool:
    """Return whether a physical table belongs to the derived layer contract."""

    return name in LAYER_TABLES


def is_silver_table(name: str) -> bool:
    """Return whether a physical table is a Silver table."""

    return name in SILVER_TABLES


def is_gold_table(name: str) -> bool:
    """Return whether a physical table is a Gold table."""

    return name in GOLD_TABLES


__all__ = [
    "GOLD_TABLES",
    "LAYER_TABLES",
    "REGISTRY_TABLE",
    "SILVER_TABLES",
    "build_gold",
    "build_silver",
    "gold_table_name",
    "is_gold_table",
    "is_layer_table",
    "is_silver_table",
    "latest_declaration_keys",
    "layer_table_names",
    "load_bronze_history",
    "load_registry",
    "registry_schema",
    "silver_table_name",
    "source_table_from_layer",
    "upsert_registry",
]
