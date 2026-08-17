"""Small dependency-injected runner for the finite HATVP batch pipeline."""

from __future__ import annotations

import json
import logging
import tempfile
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import Settings
from .download import DownloadedFile, download_to_path
from .parser import parse_sources
from .pipeline_artifacts import archive_raw, write_report, write_tables
from .pipeline_state import (
    PipelineFailure,
    build_metadata,
    load_state,
    reuse_snapshot_metadata,
    same_snapshot,
    write_state,
)
from .quality import QualityResult, run_quality_checks
from .storage import ArtifactStore, GCSArtifactStore, LocalArtifactStore
from .table_columns import TABLE_COLUMNS
from .table_schema import PARQUET_SCHEMAS

logger = logging.getLogger("hatvp")


def snapshot_date() -> str:
    return datetime.now(ZoneInfo("Europe/Paris")).date().isoformat()


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


def run_pipeline(
    settings: Settings,
    *,
    dry_run: bool = False,
    force: bool = False,
    downloader: Callable[..., DownloadedFile] = download_to_path,
    parser: Callable[..., dict] = parse_sources,
    quality_runner: Callable[..., QualityResult] = run_quality_checks,
    bq_loader: Callable[..., None] | None = None,
    snapshot_date_provider: Callable[[], str] = snapshot_date,
    store_factory: Callable[..., ArtifactStore] = default_store,
) -> str:
    if not dry_run:
        settings.validate_storage()
    store = store_factory(settings, dry_run=dry_run)
    date = snapshot_date_provider()
    started = time.perf_counter()
    previous = load_state(store) if not dry_run else {}
    with tempfile.TemporaryDirectory(prefix="hatvp-run-") as directory:
        working_dir = Path(directory)
        downloaded = _download(settings, working_dir, downloader)
        _log_hashes(previous, downloaded, date)
        if not force and not dry_run and previous and same_snapshot(previous, downloaded):
            logger.info(
                "pipeline_complete", extra={"event": "pipeline_complete", "status": "NO_CHANGE"}
            )
            return "NO_CHANGE"
        metadata = reuse_snapshot_metadata(
            store, date, build_metadata(date, settings, downloaded), dry_run
        )
        archive_raw(store, date, downloaded, metadata, dry_run)
        tables = parser(downloaded["liste.csv"].path, downloaded["declarations.xml"].path, date)
        previous_report = _previous_report(store, previous, dry_run)
        quality = quality_runner(tables, previous_report=previous_report, snapshot_date=date)
        write_report(store, date, quality, dry_run)
        files = write_tables(store, tables, date, working_dir, dry_run)
        if quality.has_errors:
            raise PipelineFailure(
                f"Quality checks failed: {quality.report['quality']['errors']} error(s)"
            )
        _load_bigquery(settings, files, date, dry_run, bq_loader)
        if not dry_run:
            write_state(
                store,
                {
                    "snapshot_date": date,
                    "fetched_at": metadata["fetched_at"],
                    "xml_sha256": downloaded["declarations.xml"].sha256,
                    "csv_sha256": downloaded["liste.csv"].sha256,
                    "pipeline_git_sha": settings.pipeline_git_sha,
                    "pipeline_version": settings.pipeline_version,
                },
            )
        status = "SUCCESS_WITH_WARNINGS" if quality.has_warnings else "SUCCESS"
        logger.info(
            "pipeline_complete",
            extra={
                "event": "pipeline_complete",
                "status": status,
                "snapshot_date": date,
                "elapsed_seconds": round(time.perf_counter() - started, 3),
            },
        )
        return status


def _download(
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


def _previous_report(store: ArtifactStore, previous: dict, dry_run: bool) -> dict | None:
    if dry_run or not previous.get("snapshot_date"):
        return None
    path = f"quality/snapshot_date={previous['snapshot_date']}/report.json"
    return json.loads(store.read_bytes(path)) if store.exists(path) else None


def _log_hashes(previous: dict, downloaded: dict[str, DownloadedFile], date: str) -> None:
    logger.info(
        "hash_comparison",
        extra={
            "event": "hash_comparison",
            "previous_xml_sha256": previous.get("xml_sha256"),
            "previous_csv_sha256": previous.get("csv_sha256"),
            "new_xml_sha256": downloaded["declarations.xml"].sha256,
            "new_csv_sha256": downloaded["liste.csv"].sha256,
            "snapshot_date": date,
        },
    )


def _load_bigquery(
    settings: Settings,
    files: dict[str, Path],
    date: str,
    dry_run: bool,
    loader: Callable[..., None] | None,
) -> None:
    if not settings.hatvp_enable_bigquery:
        return
    if dry_run:
        logger.info("bigquery_skipped", extra={"event": "bigquery_skipped", "reason": "dry_run"})
        return
    if not settings.bigquery_project:
        raise PipelineFailure("HATVP_BIGQUERY_PROJECT is required when BigQuery is enabled")
    from .bigquery import CURATED_TABLES, load_parquet_tables

    loader = loader or load_parquet_tables
    uris = (
        None
        if settings.local_output or not settings.hatvp_bucket
        else {
            name: f"gs://{settings.hatvp_bucket}/{settings.hatvp_prefix}/silver/{name}/snapshot_date={date}/data.parquet"
            for name in CURATED_TABLES
        }
    )
    loader(
        project=settings.bigquery_project,
        dataset=settings.hatvp_bigquery_dataset,
        table_files=files,
        snapshot_date=date,
        gcs_uris=uris,
        table_names=CURATED_TABLES,
        location=settings.hatvp_bigquery_location,
    )
    logger.info(
        "bigquery_load_complete",
        extra={
            "event": "bigquery_load_complete",
            "tables": list(CURATED_TABLES),
            "snapshot_date": date,
            "location": settings.hatvp_bigquery_location,
        },
    )


__all__ = [
    "PARQUET_SCHEMAS",
    "TABLE_COLUMNS",
    "PipelineFailure",
    "default_store",
    "run_pipeline",
    "snapshot_date",
]
