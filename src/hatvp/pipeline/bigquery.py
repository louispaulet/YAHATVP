"""BigQuery-specific pipeline step and URI construction."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ..bigquery import CURATED_TABLES, load_parquet_tables
from ..config import Settings

logger = logging.getLogger("hatvp")


def curated_gcs_uris(settings: Settings, snapshot: str) -> dict[str, str] | None:
    """Return canonical silver URIs when the run writes to GCS."""

    if settings.local_output or not settings.hatvp_bucket:
        return None
    return {
        name: (
            f"gs://{settings.hatvp_bucket}/{settings.hatvp_prefix}/silver/{name}/"
            f"snapshot_date={snapshot}/data.parquet"
        )
        for name in CURATED_TABLES
    }


def load_bigquery(
    settings: Settings,
    files: dict[str, Path],
    snapshot: str,
    dry_run: bool,
    loader: Any | None,
) -> None:
    """Load curated tables unless disabled or running in dry-run mode."""

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
        table_names=CURATED_TABLES,
        location=settings.hatvp_bigquery_location,
    )
    logger.info(
        "bigquery_load_complete",
        extra={
            "event": "bigquery_load_complete",
            "tables": list(CURATED_TABLES),
            "snapshot_date": snapshot,
            "location": settings.hatvp_bigquery_location,
        },
    )


def curated_file_names(files: dict[str, Path]) -> tuple[str, ...]:
    """Return the curated files present in a pipeline artifact mapping."""

    return tuple(name for name in CURATED_TABLES if name in files)


__all__ = ["curated_file_names", "curated_gcs_uris", "load_bigquery"]
