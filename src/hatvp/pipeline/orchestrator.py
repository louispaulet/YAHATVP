"""Cascade the raw-ingestion and retained-source processing stages."""

from __future__ import annotations

from collections.abc import Callable

from ..config import Settings
from ..download import DownloadedFile, download_to_path
from ..parser import parse_sources
from ..quality import QualityResult, run_quality_checks
from ..storage import ArtifactStore
from .ingestion import ingest_official
from .legacy import run_legacy
from .processing import process_sources
from .result import log_no_change
from .source_contract import load_source_state, source_ids
from .state import PipelineFailure, load_state
from .steps import default_store


def run_pipeline(
    settings: Settings,
    *,
    dry_run: bool = False,
    force: bool = False,
    downloader: Callable[..., DownloadedFile] = download_to_path,
    parser: Callable[..., dict] = parse_sources,
    quality_runner: Callable[..., QualityResult] = run_quality_checks,
    bq_loader: Callable[..., None] | None = None,
    snapshot_date_provider: Callable[[], str],
    store_factory: Callable[..., ArtifactStore] = default_store,
) -> str:
    """Run official ingestion and cascade into combined-source processing."""

    snapshot = snapshot_date_provider()
    if dry_run:
        return run_legacy(
            settings,
            dry_run=True,
            force=force,
            downloader=downloader,
            parser=parser,
            quality_runner=quality_runner,
            bq_loader=bq_loader,
            snapshot=snapshot,
            store_factory=store_factory,
        )
    settings.validate_storage()
    store = store_factory(settings, dry_run=False)
    status = ingest_official(settings, snapshot, store, downloader=downloader, force=force)
    if status == "NO_CHANGE" and _processed_state_is_current(store):
        log_no_change()
        return "NO_CHANGE"
    return process_sources(
        settings,
        snapshot,
        store,
        parser=parser,
        quality_runner=quality_runner,
        bq_loader=bq_loader,
    )


def _processed_state_is_current(store: ArtifactStore) -> bool:
    processed = load_state(store)
    snapshots = processed.get("source_snapshots") or {}
    ids = source_ids(store)
    if snapshots and set(snapshots) >= set(ids):
        return all(
            snapshots[source].get("files") == load_source_state(store, source).get("files")
            for source in ids
        )
    official = load_source_state(store, "hatvp_website")
    return (
        bool(official)
        and processed.get("xml_sha256") == official.get("xml_sha256")
        and processed.get("csv_sha256") == official.get("csv_sha256")
    )


__all__ = ["PipelineFailure", "run_pipeline"]
