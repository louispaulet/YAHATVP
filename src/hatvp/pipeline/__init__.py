from __future__ import annotations

import tempfile
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from ..config import Settings
from ..download import DownloadedFile, download_to_path
from ..layers import load_bronze_history, load_registry
from ..parser import parse_sources
from ..quality import QualityResult, run_quality_checks
from ..storage import ArtifactStore
from .artifacts import archive_raw, write_report
from .flow import build_layers
from .result import finish_run, log_no_change
from .state import (
    PipelineFailure,
    build_metadata,
    load_state,
    reuse_snapshot_metadata,
    same_snapshot,
)
from .state_update import write_success_state
from .steps import (
    default_store,
    download_sources,
    load_bigquery,
    log_hashes,
    previous_report,
)

__all__ = ["PipelineFailure", "default_store", "run_pipeline", "snapshot_date"]


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
    history = load_bronze_history(store) if not dry_run else {}
    registry = load_registry(store) if not dry_run else []
    with tempfile.TemporaryDirectory(prefix="hatvp-run-") as directory:
        working_dir = Path(directory)
        downloaded = download_sources(settings, working_dir, downloader)
        log_hashes(previous, downloaded, snapshot)
        if not force and not dry_run and previous and same_snapshot(previous, downloaded):
            log_no_change()
            return "NO_CHANGE"
        metadata = reuse_snapshot_metadata(
            store, snapshot, build_metadata(snapshot, settings, downloaded), dry_run
        )
        archive_raw(store, snapshot, downloaded, metadata, dry_run)
        tables = parser(
            downloaded["liste.csv"].path,
            downloaded["declarations.xml"].path,
            snapshot,
            source_metadata=metadata["source_metadata"],
        )
        quality = quality_runner(
            tables,
            previous_report=previous_report(store, previous, dry_run),
            snapshot_date=snapshot,
        )
        write_report(store, snapshot, quality, dry_run)
        if quality.has_errors:
            raise PipelineFailure(
                f"Quality checks failed: {quality.report['quality']['errors']} error(s)"
            )
        files = build_layers(store, tables, history, registry, snapshot, working_dir, dry_run)
        load_bigquery(settings, files, snapshot, dry_run, bq_loader)
        if not dry_run:
            write_success_state(store, snapshot, metadata, downloaded, settings)
        return finish_run(snapshot, started, quality)
