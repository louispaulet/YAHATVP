"""End-to-end fixture check for current cumulative layer partitions."""

from datetime import date
from pathlib import Path

import polars as pl

from hatvp.pipeline.flow import build_layers
from hatvp.storage import LocalArtifactStore


def declaration(key: str, depot: str, raw: str, observed: str) -> dict:
    return {
        "bronze_record_key": key,
        "declaration_uuid": "shared-uuid",
        "declarant_key": "person-1",
        "snapshot_date": observed[:10],
        "source_snapshot_date": observed[:10],
        "source_observed_at": observed,
        "source_format": "xml",
        "ingestion_source": "hatvp_website",
        "raw_record_json": raw,
        "date_depot": depot,
        "date_debut_mandat": "2020-01-01",
        "mandat_label": "Maire",
    }


def person(key: str, observed: str) -> dict:
    return {
        "bronze_record_key": key,
        "declaration_uuid": "shared-uuid",
        "snapshot_date": observed[:10],
        "source_snapshot_date": observed[:10],
        "source_observed_at": observed,
        "ingestion_source": "hatvp_website",
        "source_format": "xml",
        "nom": key.upper(),
        "prenom": "Test",
    }


def test_layer_files_keep_withdrawn_version_in_bronze_and_silver(tmp_path: Path) -> None:
    """Gold uses the online amendment while lower layers retain both versions."""

    old = declaration("old", "2025-01-01", '{"v":1}', "2025-01-02T08:00:00+00:00")
    new = declaration("new", "2026-01-01", '{"v":2}', "2026-02-01T08:00:00+00:00")
    history = {
        "declarations": [old],
        "people": [person("old", old["source_observed_at"])],
        "incomes": [],
        "assets": [],
    }
    current = {
        "declarations": [new],
        "people": [person("new", new["source_observed_at"])],
        "incomes": [],
        "assets": [],
    }
    store = LocalArtifactStore(tmp_path / "store", "hatvp")
    work = tmp_path / "work"
    work.mkdir()

    files = build_layers(store, current, history, [], "2026-03-01", work, False)
    layers = ("declarations", "silver_declarations", "gold_declarations")
    assert len({files[name] for name in layers}) == len(layers)
    bronze = pl.read_parquet(files["declarations"])
    silver = pl.read_parquet(files["silver_declarations"])
    gold = pl.read_parquet(files["gold_declarations"])

    assert set(bronze["bronze_record_key"]) == {"old", "new"}
    assert set(silver["bronze_record_key"]) == {"old", "new"}
    old_status = bronze.filter(pl.col("bronze_record_key") == "old")["publication_status"][0]
    assert old_status == "unpublished"
    assert gold["bronze_record_key"].to_list() == ["new"]
    assert bronze["snapshot_date"].unique().to_list() == [date(2026, 3, 1)]
