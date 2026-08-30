"""Read retained Bronze partitions for historical anomaly comparisons."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import polars as pl

from ..storage import ArtifactStore

HISTORY_TABLES = ("declarations", "people", "incomes", "assets")


def load_bronze_history(store: ArtifactStore) -> dict[str, list[dict[str, Any]]]:
    """Load every retained local/GCS Bronze partition, with legacy fallback."""

    history: dict[str, list[dict[str, Any]]] = {name: [] for name in HISTORY_TABLES}
    list_paths = getattr(store, "list_paths", None)
    if list_paths is None:
        return history
    for name in HISTORY_TABLES:
        paths = [
            *list_paths(f"bronze/{name}/"),
            *list_paths(f"silver/{name}/"),
        ]
        for path in sorted(paths):
            if not path.endswith("data.parquet"):
                continue
            history[name].extend(_read_partition(store, path))
    return history


def load_registry(store: ArtifactStore) -> list[dict[str, Any]]:
    """Load retained registry partitions for idempotent lifecycle updates."""

    list_paths = getattr(store, "list_paths", None)
    if list_paths is None:
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(list_paths("anomaly_registry/")):
        if path.endswith("data.parquet"):
            rows.extend(_read_partition(store, path))
    return _latest_registry_rows(rows)


def _read_partition(store: ArtifactStore, path: str) -> list[dict[str, Any]]:
    """Read one Parquet object without requiring a cloud filesystem mount."""

    payload = store.read_bytes(path)
    return pl.read_parquet(BytesIO(payload)).to_dicts()


def history_snapshot_dates(history: dict[str, list[dict[str, Any]]]) -> tuple[str, ...]:
    """Return the retained snapshot range used in backfill evidence."""

    dates = {
        str(row.get("snapshot_date") or row.get("source_snapshot_date"))
        for rows in history.values()
        for row in rows
        if row.get("snapshot_date") or row.get("source_snapshot_date")
    }
    return tuple(sorted(dates))


def history_row_count(history: dict[str, list[dict[str, Any]]]) -> int:
    """Count all retained source rows for the quality/backfill report."""

    return sum(len(rows) for rows in history.values())


def _latest_registry_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse repeated partition copies by stable anomaly key."""

    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("anomaly_key") or row.get("anomaly_id") or "")
        if key:
            latest[key] = row
    return sorted(latest.values(), key=lambda row: str(row.get("anomaly_key")))


def local_partition_paths(root: Path, name: str) -> list[str]:
    """Return the same logical paths used by LocalArtifactStore diagnostics."""

    return [str(path) for path in root.glob(f"**/bronze/{name}/**/data.parquet")]


__all__ = [
    "HISTORY_TABLES",
    "history_row_count",
    "history_snapshot_dates",
    "load_bronze_history",
    "load_registry",
]
