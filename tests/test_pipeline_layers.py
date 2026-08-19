"""Forced replay acceptance checks for the complete local layer pipeline."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

import polars as pl

from hatvp import main as main_module
from hatvp.layers.registry_schema import registry_schema
from hatvp.main import run_pipeline
from hatvp.tables import write_parquet
from tests.pipeline_support import fixture_downloader, settings, state_path


def _fingerprint(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*.parquet"))
    }


def test_force_replay_writes_all_layers_and_unchanged_replay_is_no_change(
    tmp_path: Path, monkeypatch
) -> None:
    output = tmp_path / "output"
    monkeypatch.setattr(main_module, "_snapshot_date", lambda: "2026-08-16")
    first = run_pipeline(settings(output), force=True, downloader=fixture_downloader)
    root = output / "hatvp"

    assert first == "SUCCESS_WITH_WARNINGS"
    assert (root / "raw/snapshot_date=2026-08-16/declarations.xml").exists()
    for layer in ("bronze", "silver", "gold"):
        assert (root / f"{layer}/declarations/snapshot_date=2026-08-16/data.parquet").exists()
    registry = root / "anomaly_registry/snapshot_date=2026-08-16/data.parquet"
    assert registry.exists()
    assert (
        pl.read_parquet(root / "gold/declarations/snapshot_date=2026-08-16/data.parquet").height
        == 2
    )
    before = _fingerprint(root)
    state_before = state_path(output).read_bytes()

    replay = run_pipeline(settings(output), force=True, downloader=fixture_downloader)
    assert replay == "SUCCESS_WITH_WARNINGS"
    assert _fingerprint(root) == before
    assert state_path(output).read_bytes() == state_before
    assert run_pipeline(settings(output), downloader=fixture_downloader) == "NO_CHANGE"


def test_forced_layer_outputs_keep_source_and_anomaly_columns(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "output"
    monkeypatch.setattr(main_module, "_snapshot_date", lambda: "2026-08-16")
    run_pipeline(settings(output), force=True, downloader=fixture_downloader)
    root = output / "hatvp"
    silver = pl.read_parquet(root / "silver/incomes/snapshot_date=2026-08-16/data.parquet")
    gold = pl.read_parquet(root / "gold/incomes/snapshot_date=2026-08-16/data.parquet")
    gold_people = pl.read_parquet(root / "gold/people/snapshot_date=2026-08-16/data.parquet")
    gold_assets = pl.read_parquet(root / "gold/assets/snapshot_date=2026-08-16/data.parquet")
    assert {"raw_value", "normalized_value", "anomaly_rule_ids", "metric_eligible"} <= set(
        silver.columns
    )
    assert {"is_latest_declaration", "active_in_gold"} <= set(gold.columns)
    assert "gender" in gold_people.columns
    assert {"asset_event_date", "asset_event_precision", "asset_event_source_field"} <= set(
        gold_assets.columns
    )
    assert gold_assets.schema["asset_event_date"] == pl.Date
    assert silver.height >= gold.height


def test_registry_partition_retains_stable_keys_and_evidence(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "output"
    monkeypatch.setattr(main_module, "_snapshot_date", lambda: "2026-08-16")
    run_pipeline(settings(output), force=True, downloader=fixture_downloader)
    registry = pl.read_parquet(
        output / "hatvp/anomaly_registry/snapshot_date=2026-08-16/data.parquet"
    )

    assert {"anomaly_id", "anomaly_key", "evidence", "seen_snapshots"} <= set(registry.columns)
    assert registry["anomaly_key"].n_unique() == registry.height


def test_registry_writer_normalizes_historical_date_values(tmp_path: Path) -> None:
    path = tmp_path / "mixed-registry.parquet"
    values = [("old", "2026-08-18"), ("new", date(2026, 8, 19))]
    rows = [
        {"anomaly_key": key, "snapshot_date": value, "source_snapshot_date": value}
        for key, value in values
    ]

    write_parquet(rows, path, list(registry_schema()), registry_schema())

    frame = pl.read_parquet(path)
    assert frame.select(["snapshot_date", "source_snapshot_date"]).to_dict(as_series=False) == {
        "snapshot_date": [date(2026, 8, 18), date(2026, 8, 19)],
        "source_snapshot_date": ["2026-08-18", "2026-08-19"],
    }
