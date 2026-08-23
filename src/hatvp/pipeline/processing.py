"""Processing stage: parse retained raw sources through Bronze to Gold."""

from __future__ import annotations

import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ..config import Settings
from ..layers import load_bronze_history, load_registry
from ..parser import parse_sources
from ..quality import QualityResult, run_quality_checks
from ..storage import ArtifactStore
from .artifacts import write_report
from .flow import build_layers
from .processing_sources import RawSource, materialize_sources
from .result import finish_run
from .source_contract import OFFICIAL_SOURCE
from .state import PipelineFailure, load_state, write_state
from .steps import load_bigquery, previous_report


def process_sources(
    settings: Settings,
    snapshot: str,
    store: ArtifactStore,
    *,
    parser: Callable[..., dict[str, list[dict[str, Any]]]] = parse_sources,
    quality_runner: Callable[..., QualityResult] = run_quality_checks,
    bq_loader: Callable[..., None] | None = None,
    dry_run: bool = False,
) -> str:
    started = time.perf_counter()
    previous = load_state(store) if not dry_run else {}
    history = load_bronze_history(store) if not dry_run else {}
    registry = load_registry(store) if not dry_run else []
    with tempfile.TemporaryDirectory(prefix="hatvp-process-") as directory:
        sources = materialize_sources(store, settings, Path(directory))
        tables = _parse_all(sources, snapshot, parser)
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
        files = build_layers(store, tables, history, registry, snapshot, Path(directory), dry_run)
        load_bigquery(settings, files, snapshot, dry_run, bq_loader)
        if not dry_run:
            _write_processed_state(store, settings, snapshot, sources)
        return finish_run(snapshot, started, quality)


def _parse_all(
    sources: list[RawSource], snapshot: str, parser: Callable[..., dict]
) -> dict[str, list[dict[str, Any]]]:
    combined: dict[str, list[dict[str, Any]]] = {}
    for source in sources:
        metadata = source.metadata.get("source_metadata", {})
        parsed = parser(source.csv, source.xml, snapshot, source_metadata=metadata)
        for name, rows in parsed.items():
            combined.setdefault(name, []).extend(rows)
    return combined


def _write_processed_state(
    store: ArtifactStore, settings: Settings, snapshot: str, sources: list[RawSource]
) -> None:
    source_snapshots = {source.source_id: _source_state(source) for source in sources}
    official = next(
        (source for source in sources if source.source_id == OFFICIAL_SOURCE), sources[0]
    )
    state = {
        "snapshot_date": snapshot,
        "fetched_at": max(item.metadata.get("fetched_at", "") for item in sources),
        "xml_sha256": _hash(official, "declarations.xml"),
        "csv_sha256": _hash(official, "liste.csv"),
        "pipeline_git_sha": settings.pipeline_git_sha,
        "pipeline_version": settings.pipeline_version,
        "source_snapshots": source_snapshots,
    }
    write_state(store, state)


def _source_state(source: RawSource) -> dict[str, Any]:
    files = {item["name"]: item["sha256"] for item in source.metadata.get("files", [])}
    return {"snapshot_date": source.snapshot, "files": files, "source_id": source.source_id}


def _hash(source: RawSource, name: str) -> str | None:
    return next(
        (item["sha256"] for item in source.metadata.get("files", []) if item["name"] == name),
        None,
    )
