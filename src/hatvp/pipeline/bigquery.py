"""BigQuery-specific pipeline step and URI construction."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..bigquery import ALL_TABLES, CURATED_TABLES, load_parquet_tables
from ..config import Settings

logger = logging.getLogger("hatvp")


def curated_gcs_uris(settings: Settings, snapshot: str) -> dict[str, str] | None:
    """Return canonical GCS URIs for every physical analytical table."""

    if settings.local_output or not settings.hatvp_bucket:
        return None
    return {name: _gcs_uri(settings, name, snapshot) for name in ALL_TABLES}


def _gcs_uri(settings: Settings, name: str, snapshot: str) -> str:
    if name in CURATED_TABLES:
        layer, source = "bronze", name
    elif name.startswith("silver_"):
        layer, source = "silver", name.removeprefix("silver_")
    elif name.startswith("gold_"):
        layer, source = "gold", name.removeprefix("gold_")
    else:
        layer, source = "anomaly_registry", ""
    suffix = f"/{source}" if source else ""
    return f"gs://{settings.hatvp_bucket}/{settings.hatvp_prefix}/{layer}{suffix}/snapshot_date={snapshot}/data.parquet"


def load_bigquery(
    settings: Settings,
    files: dict[str, Path],
    snapshot: str,
    dry_run: bool,
    loader: Any | None,
) -> None:
    """Load all required analytical layers unless disabled or in dry-run mode."""

    if not settings.hatvp_enable_bigquery:
        return
    if dry_run:
        logger.info("bigquery_skipped", extra={"event": "bigquery_skipped", "reason": "dry_run"})
        return
    if not settings.bigquery_project:
        raise RuntimeError("HATVP_BIGQUERY_PROJECT is required when BigQuery is enabled")
    load = loader or load_parquet_tables
    load(
        project=settings.bigquery_project,
        dataset=settings.hatvp_bigquery_dataset,
        table_files=files,
        snapshot_date=snapshot,
        gcs_uris=curated_gcs_uris(settings, snapshot),
        table_names=ALL_TABLES,
        location=settings.hatvp_bigquery_location,
    )
    logger.info(
        "bigquery_load_complete",
        extra={
            "event": "bigquery_load_complete",
            "tables": list(ALL_TABLES),
            "snapshot_date": snapshot,
            "location": settings.hatvp_bigquery_location,
        },
    )


def curated_file_names(files: dict[str, Path]) -> tuple[str, ...]:
    """Return the curated files present in a pipeline artifact mapping."""

    return tuple(name for name in CURATED_TABLES if name in files)


def layer_file_names(files: dict[str, Path]) -> tuple[str, ...]:
    """Return all physical derived tables present in one pipeline run."""

    return tuple(name for name in ALL_TABLES if name in files)


__all__ = ["curated_file_names", "curated_gcs_uris", "layer_file_names", "load_bigquery"]
