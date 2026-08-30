"""Orchestrator regressions for source-aware processing short-circuits.

The normal official cascade must notice sources ingested between runs.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import polars as pl

from hatvp.pipeline import default_store, run_pipeline
from hatvp.pipeline.ingestion import ingest_wayback_zip
from hatvp.pipeline.orchestrator import _processed_state_is_current
from hatvp.pipeline.source_contract import write_source_state
from tests.pipeline_support import FIXTURES, fixture_downloader, settings


def archive_fixture(path: Path) -> Path:
    """Create the archive shape accepted by the Wayback ingestion boundary."""

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(FIXTURES / "declarations.xml", "declarations.xml")
    return path


def run_official(configured, snapshot: str) -> str:
    """Run the official source with a deterministic processing partition."""

    return run_pipeline(
        configured,
        downloader=fixture_downloader,
        snapshot_date_provider=lambda: snapshot,
    )


def test_new_source_invalidates_official_only_processed_state(tmp_path: Path) -> None:
    """A newly ingested archive source must trigger combined processing."""

    output = tmp_path / "output"
    configured = settings(output)
    snapshot = "2026-08-23"

    assert run_official(configured, snapshot) == "SUCCESS_WITH_WARNINGS"
    store = default_store(configured)
    archive = archive_fixture(tmp_path / "declarations.xml.zip")
    assert ingest_wayback_zip(configured, archive, snapshot, store) == "INGESTED"

    assert run_official(configured, snapshot) == "SUCCESS_WITH_WARNINGS"
    declarations = pl.read_parquet(
        output / "hatvp/bronze/declarations/snapshot_date=2026-08-23/data.parquet"
    )
    assert set(declarations["ingestion_source"].unique()) == {
        "hatvp_website",
        "wayback_github",
    }


def test_legacy_processed_state_does_not_hide_new_archive_source(tmp_path: Path) -> None:
    """Legacy official-only state is stale as soon as another source exists."""

    store = default_store(settings(tmp_path / "output"))
    store.put_bytes(
        "state/latest.json",
        json.dumps({"xml_sha256": "xml", "csv_sha256": "csv"}).encode(),
        content_type="application/json",
    )
    write_source_state(store, "wayback_github", {"files": {}})

    assert not _processed_state_is_current(store)
