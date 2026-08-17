"""CLI and compatibility boundary for the HATVP ingestion pipeline."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .bigquery import CURATED_TABLES, load_parquet_tables
from .config import Settings
from .download import DownloadedFile, download_to_path
from .json_logging import configure_logging as _configure_logging
from .parser import parse_sources
from .pipeline import default_store, snapshot_date
from .pipeline import run_pipeline as _run_pipeline
from .pipeline.state import PipelineFailure, load_state
from .quality import run_quality_checks
from .storage import ArtifactStore
from .tables import write_parquet
from .tables.columns import TABLE_COLUMNS
from .tables.schema import PARQUET_SCHEMAS

logger = logging.getLogger("hatvp")
__all__ = ["CURATED_TABLES", "DownloadedFile", "PARQUET_SCHEMAS", "PipelineFailure", "Settings", "TABLE_COLUMNS", "build_parser", "cli", "run_pipeline"]  # fmt: skip  # noqa: E501


def _snapshot_date() -> str:
    return snapshot_date()


def _store(settings: Settings, *, dry_run: bool = False) -> ArtifactStore:
    return default_store(settings, dry_run=dry_run)


def _write_parquet(
    rows: list[dict],
    path: Path,
    required_columns: list[str],
    schema: dict[str, object] | None = None,
) -> None:
    write_parquet(rows, path, required_columns, schema)


def _load_state(store: ArtifactStore) -> dict:
    return load_state(store)


def run_pipeline(
    settings: Settings, *, dry_run: bool = False, force: bool = False, downloader=download_to_path
) -> str:
    return _run_pipeline(
        settings,
        dry_run=dry_run,
        force=force,
        downloader=downloader,
        parser=parse_sources,
        quality_runner=run_quality_checks,
        bq_loader=load_parquet_tables,
        snapshot_date_provider=_snapshot_date,
        store_factory=_store,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the HATVP ingestion pipeline")
    parser.add_argument(
        "--dry-run", action="store_true", help="Process inputs without mutating outputs"
    )
    parser.add_argument(
        "--force", action="store_true", help="Reprocess even when hashes are unchanged"
    )
    parser.add_argument(
        "--local-output", type=Path, help="Write artifacts below this directory instead of GCS"
    )
    return parser


def cli(argv: list[str] | None = None) -> int:
    _configure_logging()
    args = build_parser().parse_args(argv)
    settings = (
        Settings().model_copy(update={"local_output": args.local_output})
        if args.local_output
        else Settings()
    )
    try:
        status = run_pipeline(settings, dry_run=args.dry_run, force=args.force)
    except Exception:
        logger.exception("pipeline_failed", extra={"event": "pipeline_failed", "status": "FAILED"})
        return 1
    logger.info("pipeline_status", extra={"event": "pipeline_status", "status": status})
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
