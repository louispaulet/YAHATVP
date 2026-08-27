"""Public pipeline façade for raw ingestion and analytical processing."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from ..config import Settings
from ..download import DownloadedFile, download_to_path
from ..parser import parse_sources
from ..quality import QualityResult, run_quality_checks
from ..storage import ArtifactStore
from .orchestrator import run_pipeline as _run_pipeline
from .processing import process_sources
from .source_contract import OFFICIAL_SOURCE
from .state import PipelineFailure
from .steps import default_store


def snapshot_date() -> str:
    """Return the Paris-local processing partition date."""

    return datetime.now(ZoneInfo("Europe/Paris")).date().isoformat()


def run_pipeline(
    settings: Settings,
    *,
    dry_run: bool = False,
    force: bool = False,
    downloader: Callable[..., DownloadedFile] = download_to_path,
    parser: Callable[..., dict[str, list[dict[str, Any]]]] = parse_sources,
    quality_runner: Callable[..., QualityResult] = run_quality_checks,
    bq_loader: Callable[..., None] | None = None,
    snapshot_date_provider: Callable[[], str] = snapshot_date,
    store_factory: Callable[..., ArtifactStore] = default_store,
) -> str:
    """Run the official source cascade, retaining the legacy public signature."""

    return _run_pipeline(
        settings,
        dry_run=dry_run,
        force=force,
        downloader=downloader,
        parser=parser,
        quality_runner=quality_runner,
        bq_loader=bq_loader,
        snapshot_date_provider=snapshot_date_provider,
        store_factory=store_factory,
    )


def process_pipeline(
    settings: Settings,
    *,
    snapshot: str | None = None,
    dry_run: bool = False,
    parser: Callable[..., dict[str, list[dict[str, Any]]]] = parse_sources,
    quality_runner: Callable[..., QualityResult] = run_quality_checks,
    bq_loader: Callable[..., None] | None = None,
    store_factory: Callable[..., ArtifactStore] = default_store,
) -> str:
    """Run processing against all latest raw source snapshots."""

    if not dry_run:
        settings.validate_storage()
    store = store_factory(settings, dry_run=dry_run)
    return process_sources(
        settings,
        snapshot or snapshot_date(),
        store,
        parser=parser,
        quality_runner=quality_runner,
        bq_loader=bq_loader,
        dry_run=dry_run,
    )


__all__ = [
    "OFFICIAL_SOURCE",
    "PipelineFailure",
    "default_store",
    "process_pipeline",
    "run_pipeline",
    "snapshot_date",
]
