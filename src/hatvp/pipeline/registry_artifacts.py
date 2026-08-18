"""Anomaly-registry Parquet artifact writer and path contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..layers.registry_schema import registry_schema
from ..storage import ArtifactStore
from ..tables import write_parquet

REGISTRY_ARTIFACT = "anomaly_registry"


def write_registry(
    store: ArtifactStore,
    rows: list[dict[str, Any]],
    snapshot: str,
    work: Path,
    dry_run: bool,
) -> dict[str, Path]:
    """Write one deterministic registry partition and return its load file."""

    path = work / f"{REGISTRY_ARTIFACT}.parquet"
    schema = registry_schema()
    write_parquet(rows, path, list(schema), schema)
    if not dry_run:
        store.put_file(registry_path(snapshot), path, content_type="application/vnd.apache.parquet")
    return {REGISTRY_ARTIFACT: path}


def registry_path(snapshot: str) -> str:
    """Return the logical registry object path for one snapshot."""

    return f"{REGISTRY_ARTIFACT}/snapshot_date={snapshot}/data.parquet"


def registry_file_name() -> str:
    """Return the physical table name passed to BigQuery."""

    return REGISTRY_ARTIFACT


def registry_artifact_prefix() -> str:
    """Return the stable root used by historical registry backfill."""

    return f"{REGISTRY_ARTIFACT}/"


def registry_content_type() -> str:
    """Return the Parquet MIME type used by local and cloud writers."""

    return "application/vnd.apache.parquet"


def registry_partition_key(snapshot: str) -> str:
    """Return the partition label used in backfill manifests."""

    return f"snapshot_date={snapshot}"


def registry_is_partitioned_path(path: str) -> bool:
    """Return whether a path belongs to a valid registry partition."""

    return path.startswith(f"{REGISTRY_ARTIFACT}/") and "/snapshot_date=" in path


__all__ = [
    "REGISTRY_ARTIFACT",
    "registry_artifact_prefix",
    "registry_file_name",
    "registry_path",
    "write_registry",
]
