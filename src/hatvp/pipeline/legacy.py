"""Compatibility implementation for fixture-backed dry runs."""

from __future__ import annotations

import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from ..config import Settings
from ..download import DownloadedFile
from ..layers import load_bronze_history, load_registry
from ..quality import QualityResult
from ..storage import ArtifactStore
from .artifacts import archive_raw, write_report
from .flow import build_layers
from .result import finish_run, log_no_change
from .state import (
    PipelineFailure,
    build_metadata,
    load_state,
    reuse_snapshot_metadata,
)
from .state_update import write_success_state
from .steps import download_sources, load_bigquery, log_hashes, previous_report


def run_legacy(
    settings: Settings,
    *,
    dry_run: bool,
    force: bool,
    downloader: Callable[..., DownloadedFile],
    parser: Callable[..., dict],
    quality_runner: Callable[..., QualityResult],
    bq_loader: Callable[..., None] | None,
    snapshot: str,
    store_factory: Callable[..., ArtifactStore],
) -> str:
    """Keep the old temporary-input path available for local dry runs."""

    store = store_factory(settings, dry_run=dry_run)
    previous = load_state(store) if not dry_run else {}
    history = load_bronze_history(store) if not dry_run else {}
    registry = load_registry(store) if not dry_run else []
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="hatvp-run-") as directory:
        downloaded = download_sources(settings, Path(directory), downloader)
        log_hashes(previous, downloaded, snapshot)
        unchanged = (
            previous.get("xml_sha256") == downloaded["declarations.xml"].sha256
            and previous.get("csv_sha256") == downloaded["liste.csv"].sha256
        )
        if not force and not dry_run and previous and unchanged:
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
        files = build_layers(
            store,
            tables,
            history,
            registry,
            snapshot,
            Path(directory),
            dry_run,
            settings.hatvp_person_dob_max_age_years,
        )
        load_bigquery(settings, files, snapshot, dry_run, bq_loader)
        if not dry_run:
            write_success_state(store, snapshot, metadata, downloaded, settings)
        return finish_run(snapshot, started, quality)


__all__ = ["run_legacy"]
