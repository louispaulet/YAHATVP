"""Raw-source split, archive retention, and pre-anomaly dedupe contracts."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import polars as pl
import pytest

from hatvp.layers.quality_selection import dedupe_for_quality, quality_declaration_count
from hatvp.pipeline import process_pipeline
from hatvp.pipeline.ingestion import ingest_wayback_zip
from hatvp.pipeline.source_contract import load_source_state, source_ids
from hatvp.pipeline.state import PipelineFailure
from tests.pipeline_support import FIXTURES, fixture_downloader, settings


def _archive(path: Path) -> Path:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as output:
        output.write(FIXTURES / "declarations.xml", "declarations.xml")
    return path


def test_official_ingestion_only_writes_immutable_raw_files(tmp_path: Path) -> None:
    output = tmp_path / "output"
    configured = settings(output)

    from hatvp.pipeline.ingestion import ingest_official

    assert (
        ingest_official(
            configured,
            "2026-08-23",
            configured_store(configured),
            downloader=fixture_downloader,
        )
        == "INGESTED"
    )
    root = output / "hatvp"
    assert (root / "raw/snapshot_date=2026-08-23/declarations.xml").exists()
    assert not (root / "gold/declarations/snapshot_date=2026-08-23/data.parquet").exists()
    assert not (root / "state/latest.json").exists()


def test_archive_ingestion_preserves_zip_and_processing_tags_source(tmp_path: Path) -> None:
    output = tmp_path / "output"
    archive = _archive(tmp_path / "declarations.xml.zip")
    configured = settings(output)
    store = configured_store(configured)

    assert ingest_wayback_zip(configured, archive, "2026-08-23", store) == "INGESTED"
    assert process_pipeline(configured, snapshot="2026-08-23") == "SUCCESS_WITH_WARNINGS"
    root = output / "hatvp"
    assert (
        root / "raw/source=wayback_github/snapshot_date=2026-08-23/declarations.xml.zip"
    ).exists()
    state = load_source_state(store, "wayback_github")
    assert state["archive_sha256"]
    declarations = pl.read_parquet(
        root / "bronze/declarations/snapshot_date=2026-08-23/data.parquet"
    )
    assert declarations["ingestion_source"].unique().to_list() == ["wayback_github"]
    assert json.loads((root / "state/latest.json").read_text())["source_snapshots"][
        "wayback_github"
    ]


def test_quality_selection_deduplicates_uuid_before_anomaly_input() -> None:
    older = {"declaration_uuid": "same", "bronze_record_key": "old", "date_depot": "2024-01-01"}
    newer = {"declaration_uuid": "same", "bronze_record_key": "new", "date_depot": "2025-01-01"}
    current = {"declarations": [older, newer], "people": [], "incomes": [], "assets": []}

    filtered, _ = dedupe_for_quality(current, {})

    assert quality_declaration_count(current, {}) == 1
    assert filtered["declarations"] == [newer]


def test_archive_snapshot_rejects_different_bytes(tmp_path: Path) -> None:
    output = tmp_path / "output"
    archive = _archive(tmp_path / "declarations.xml.zip")
    changed = tmp_path / "changed.zip"
    changed.write_bytes(archive.read_bytes() + b"changed")
    configured = settings(output)
    store = configured_store(configured)

    ingest_wayback_zip(configured, archive, "2026-08-23", store)
    with pytest.raises(PipelineFailure, match="different source hashes"):
        ingest_wayback_zip(configured, changed, "2026-08-23", store)


def test_source_discovery_keeps_legacy_official_state_with_archive_source(tmp_path: Path) -> None:
    store = configured_store(settings(tmp_path / "output"))
    store.put_bytes("state/latest.json", b'{"snapshot_date":"2026-08-23"}\n')
    store.put_bytes(
        "state/sources/wayback_github/latest.json",
        b'{"source_id":"wayback_github","snapshot_date":"2026-08-23"}\n',
    )

    assert source_ids(store) == ("hatvp_website", "wayback_github")


def configured_store(settings):
    from hatvp.pipeline import default_store

    return default_store(settings)
