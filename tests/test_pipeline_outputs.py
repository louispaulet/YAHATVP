"""Normalized Parquet, state, and immutable raw-artifact tests."""

import json
from pathlib import Path

import polars as pl
import pytest

from hatvp.main import PARQUET_SCHEMAS, TABLE_COLUMNS, PipelineFailure, _write_parquet, run_pipeline
from tests.pipeline_support import (
    FIXTURES,
    changed_fixture,
    downloader_for,
    fixture_downloader,
    raw_path,
    settings,
    state_path,
    warning_status,
)


def test_changed_xml_hash_triggers_processing(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "output"
    changed_xml = changed_fixture(
        FIXTURES / "declarations.xml",
        tmp_path / "changed.xml",
        b"fixture-uuid-1",
        b"fixture-changed",
    )
    dates = iter(("2026-08-16", "2026-08-17"))
    monkeypatch.setattr("hatvp.main._snapshot_date", lambda: next(dates))
    warning_status(run_pipeline(settings(output), downloader=fixture_downloader))
    first = json.loads(state_path(output).read_text())
    warning_status(
        run_pipeline(settings(output), downloader=downloader_for(xml_source=changed_xml))
    )
    second = json.loads(state_path(output).read_text())

    assert second["xml_sha256"] != first["xml_sha256"]
    assert second["snapshot_date"] == "2026-08-17"


def test_changed_csv_hash_triggers_processing(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "output"
    changed_csv = changed_fixture(
        FIXTURES / "liste.csv", tmp_path / "changed.csv", b"SOURCE-1", b"SOURCE-1-changed"
    )
    dates = iter(("2026-08-16", "2026-08-17"))
    monkeypatch.setattr("hatvp.main._snapshot_date", lambda: next(dates))
    warning_status(run_pipeline(settings(output), downloader=fixture_downloader))
    first = json.loads(state_path(output).read_text())
    warning_status(
        run_pipeline(settings(output), downloader=downloader_for(csv_source=changed_csv))
    )
    second = json.loads(state_path(output).read_text())

    assert second["csv_sha256"] != first["csv_sha256"]
    assert second["snapshot_date"] == "2026-08-17"


def test_curated_parquet_schema_is_stable_for_empty_and_null_only_rows(tmp_path: Path) -> None:
    empty_path = tmp_path / "empty-incomes.parquet"
    _write_parquet([], empty_path, TABLE_COLUMNS["incomes"], PARQUET_SCHEMAS["incomes"])
    empty_schema = pl.read_parquet_schema(empty_path)
    assert empty_schema["snapshot_date"] == pl.Date
    assert empty_schema["normalized_value"] == pl.Float64
    assert empty_schema["raw_value"] == pl.String
    null_path = tmp_path / "null-people.parquet"
    _write_parquet(
        [{"declaration_uuid": "fixture", "snapshot_date": "2026-08-17", "email": None}],
        null_path,
        TABLE_COLUMNS["people"],
        PARQUET_SCHEMAS["people"],
    )
    assert pl.read_parquet_schema(null_path)["email"] == pl.String


def test_immutable_raw_snapshot_rejects_different_bytes_for_same_date(
    tmp_path: Path, monkeypatch
) -> None:
    output = tmp_path / "output"
    changed_csv = changed_fixture(
        FIXTURES / "liste.csv", tmp_path / "changed.csv", b"SOURCE-1", b"SOURCE-1-conflict"
    )
    monkeypatch.setattr("hatvp.main._snapshot_date", lambda: "2026-08-16")
    warning_status(run_pipeline(settings(output), downloader=fixture_downloader))
    previous_state = state_path(output).read_bytes()

    with pytest.raises(PipelineFailure, match="Immutable raw snapshot 2026-08-16"):
        run_pipeline(settings(output), downloader=downloader_for(csv_source=changed_csv))
    assert state_path(output).read_bytes() == previous_state
    assert (
        raw_path(output, "2026-08-16", "liste.csv").read_bytes()
        == (FIXTURES / "liste.csv").read_bytes()
    )
