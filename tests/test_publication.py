"""Publication lifecycle, cumulative partitions, and Gold retention contracts."""

from datetime import UTC, datetime

import polars as pl

from hatvp.layers.gold import build_gold
from hatvp.layers.gold_selection import latest_declaration_keys
from hatvp.layers.publication import publication_snapshot
from hatvp.tables import write_table


def declaration(key, depot, raw, observed):
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


def child(key, observed):
    return {
        "bronze_record_key": key,
        "declaration_uuid": "shared-uuid",
        "snapshot_date": observed[:10],
        "source_snapshot_date": observed[:10],
        "source_observed_at": observed,
        "source_format": "xml",
        "ingestion_source": "hatvp_website",
        "raw_value": "1200",
        "income_stream": "mandate_remuneration",
        "source_section": "revenuMandatDto",
        "income_year": "2024",
    }


def test_unpublished_versions_are_cumulative_and_suppressed_only_by_online_version(tmp_path):
    old = declaration("old", "2025-01-01", '{"version":1}', "2025-01-02T08:00:00+00:00")
    new = declaration("new", "2026-01-01", '{"version":2}', "2026-01-02T08:00:00+00:00")
    history = {name: [] for name in ("declarations", "people", "incomes", "assets")}
    history["declarations"] = [old]
    history["people"] = [{**child("old", old["source_observed_at"]), "nom": "Old"}]
    current = {name: [] for name in history}
    current["declarations"] = [new]
    current["people"] = [{**child("new", new["source_observed_at"]), "nom": "New"}]

    latest = publication_snapshot(current, history, "2026-02-01")
    parents = {row["bronze_record_key"]: row for row in latest["declarations"]}

    assert set(parents) == {"old", "new"}
    assert parents["old"]["publication_status"] == "unpublished"
    assert parents["old"]["first_online_at"] == datetime(2025, 1, 2, 8, tzinfo=UTC)
    assert parents["old"]["missing_from_latest_export_at"].date().isoformat() == "2026-01-02"
    assert parents["new"]["publication_status"] == "online"
    assert parents["new"]["missing_from_latest_export_at"] is None
    assert latest["people"][0]["publication_status"] == "unpublished"
    assert {row["snapshot_date"] for row in latest["people"]} == {"2026-02-01"}
    assert latest_declaration_keys(latest["declarations"]) == {"new"}

    withdrawn = publication_snapshot({}, latest, "2026-03-01")
    assert {row["publication_status"] for row in withdrawn["declarations"]} == {"unpublished"}
    assert latest_declaration_keys(withdrawn["declarations"]) == {"old", "new"}
    withdrawn["declarations"][0]["anomaly_status"] = "superseded"
    gold, _ = build_gold(withdrawn, [])
    assert gold["declarations"][0]["active_in_gold"] is True

    reappeared = publication_snapshot(current, withdrawn, "2026-04-01")
    new_state = next(row for row in reappeared["declarations"] if row["bronze_record_key"] == "new")
    assert new_state["publication_status"] == "online"
    assert new_state["missing_from_latest_export_at"] is None

    path = tmp_path / "declarations.parquet"
    write_table(latest["declarations"], "declarations", path)
    frame = pl.read_parquet(path)
    assert frame.schema["first_online_at"] == pl.Datetime(time_unit="us", time_zone="UTC")
    assert frame["publication_status"].to_list() == ["unpublished", "online"]
