"""Independent pipeline steps for source acquisition and cloud loading."""

from __future__ import annotations

import json
import logging
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .bigquery import CURATED_TABLES, load_parquet_tables
from .config import Settings
from .download import DownloadedFile
from .storage import ArtifactStore, GCSArtifactStore, LocalArtifactStore

logger = logging.getLogger("hatvp")


def default_store(settings: Settings, dry_run: bool = False) -> ArtifactStore:
    if settings.local_output is not None:
        return LocalArtifactStore(settings.local_output, settings.hatvp_prefix)
    if dry_run:
        return LocalArtifactStore(
            Path(tempfile.mkdtemp(prefix="hatvp-dry-run-")), settings.hatvp_prefix
        )
    if not settings.hatvp_bucket:
        raise ValueError("HATVP_BUCKET is required unless --local-output is used")
    return GCSArtifactStore(settings.hatvp_bucket, settings.hatvp_prefix)


def download_sources(
    settings: Settings, directory: Path, downloader: Callable[..., DownloadedFile]
) -> dict[str, DownloadedFile]:
    kwargs = {
        "user_agent": settings.user_agent,
        "connect_timeout_seconds": settings.download_connect_timeout_seconds,
        "read_timeout_seconds": settings.download_read_timeout_seconds,
        "retries": settings.download_retries,
    }
    return {
        "liste.csv": downloader(
            settings.hatvp_csv_url, "liste.csv", directory / "liste.csv", **kwargs
        ),
        "declarations.xml": downloader(
            settings.hatvp_xml_url, "declarations.xml", directory / "declarations.xml", **kwargs
        ),
    }


def previous_report(store: ArtifactStore, previous: dict[str, Any], dry_run: bool) -> dict | None:
    if dry_run or not previous.get("snapshot_date"):
        return None
    path = f"quality/snapshot_date={previous['snapshot_date']}/report.json"
    return json.loads(store.read_bytes(path)) if store.exists(path) else None


def log_hashes(
    previous: dict[str, Any], downloaded: dict[str, DownloadedFile], snapshot: str
) -> None:
    logger.info(
        "hash_comparison",
        extra={
            "event": "hash_comparison",
            "previous_xml_sha256": previous.get("xml_sha256"),
            "previous_csv_sha256": previous.get("csv_sha256"),
            "new_xml_sha256": downloaded["declarations.xml"].sha256,
            "new_csv_sha256": downloaded["liste.csv"].sha256,
            "snapshot_date": snapshot,
        },
    )


def load_bigquery(
    settings: Settings,
    files: dict[str, Path],
    snapshot: str,
    dry_run: bool,
    loader: Callable[..., None] | None,
) -> None:
    if not settings.hatvp_enable_bigquery:
        return
    if dry_run:
        logger.info("bigquery_skipped", extra={"event": "bigquery_skipped", "reason": "dry_run"})
        return
    if not settings.bigquery_project:
        raise RuntimeError("HATVP_BIGQUERY_PROJECT is required when BigQuery is enabled")
    loader = loader or load_parquet_tables
    uris = (
        None
        if settings.local_output or not settings.hatvp_bucket
        else {
            name: f"gs://{settings.hatvp_bucket}/{settings.hatvp_prefix}/silver/{name}/snapshot_date={snapshot}/data.parquet"
            for name in CURATED_TABLES
        }
    )
    loader(
        project=settings.bigquery_project,
        dataset=settings.hatvp_bigquery_dataset,
        table_files=files,
        snapshot_date=snapshot,
        gcs_uris=uris,
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


__all__ = ["default_store", "download_sources", "load_bigquery", "log_hashes", "previous_report"]
