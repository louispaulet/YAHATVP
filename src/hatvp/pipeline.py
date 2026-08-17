"""Small dependency-injected runner for the finite HATVP batch pipeline."""

from __future__ import annotations

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
from .pipeline_steps import (
    default_store,
    download_sources,
    load_bigquery,
    log_hashes,
    previous_report,
)
from .quality import QualityResult, run_quality_checks
from .storage import ArtifactStore

logger = logging.getLogger("hatvp")


def snapshot_date() -> str:
    return datetime.now(ZoneInfo("Europe/Paris")).date().isoformat()


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
    snapshot = snapshot_date_provider()
    started = time.perf_counter()
    previous = load_state(store) if not dry_run else {}
    with tempfile.TemporaryDirectory(prefix="hatvp-run-") as directory:
        working_dir = Path(directory)
        downloaded = download_sources(settings, working_dir, downloader)
        log_hashes(previous, downloaded, snapshot)
        if not force and not dry_run and previous and same_snapshot(previous, downloaded):
            logger.info(
                "pipeline_complete", extra={"event": "pipeline_complete", "status": "NO_CHANGE"}
            )
            return "NO_CHANGE"
        metadata = reuse_snapshot_metadata(
            store, snapshot, build_metadata(snapshot, settings, downloaded), dry_run
        )
        archive_raw(store, snapshot, downloaded, metadata, dry_run)
        tables = parser(downloaded["liste.csv"].path, downloaded["declarations.xml"].path, snapshot)
        quality = quality_runner(
            tables,
            previous_report=previous_report(store, previous, dry_run),
            snapshot_date=snapshot,
        )
        write_report(store, snapshot, quality, dry_run)
        files = write_tables(store, tables, snapshot, working_dir, dry_run)
        if quality.has_errors:
            raise PipelineFailure(
                f"Quality checks failed: {quality.report['quality']['errors']} error(s)"
            )
        load_bigquery(settings, files, snapshot, dry_run, bq_loader)
        if not dry_run:
            write_state(
                store,
                {
                    "snapshot_date": snapshot,
                    "fetched_at": metadata["fetched_at"],
                    "xml_sha256": downloaded["declarations.xml"].sha256,
                    "csv_sha256": downloaded["liste.csv"].sha256,
                    "pipeline_git_sha": settings.pipeline_git_sha,
                    "pipeline_version": settings.pipeline_version,
                },
            )
        return _finish(snapshot, started, quality)


def _finish(snapshot: str, started: float, quality: QualityResult) -> str:
    status = "SUCCESS_WITH_WARNINGS" if quality.has_warnings else "SUCCESS"
    logger.info(
        "pipeline_complete",
        extra={
            "event": "pipeline_complete",
            "status": status,
            "snapshot_date": snapshot,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        },
    )
    return status


__all__ = ["PipelineFailure", "default_store", "run_pipeline", "snapshot_date"]
