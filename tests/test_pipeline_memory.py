"""Memory lifetime contracts around the source-to-Silver handoff."""

from pathlib import Path

from hatvp.layers import SILVER_TABLES
from hatvp.pipeline import flow


def _exercise_build(monkeypatch, tables):
    observed = {}

    def write_bronze(_store, rows, *_args, **_kwargs):
        observed["bronze"] = set(rows)
        observed["bronze_rows"] = {name: id(values) for name, values in rows.items()}
        return {}

    def build_silver(current, *_args, **_kwargs):
        observed["silver"] = set(current)
        observed["silver_rows"] = {name: id(rows) for name, rows in current.items()}
        return {name: [] for name in SILVER_TABLES}, {}, []

    monkeypatch.setattr(flow, "write_bronze_tables", write_bronze)
    monkeypatch.setattr(flow, "build_silver", build_silver)
    monkeypatch.setattr(flow, "build_gold", lambda *_args: ({}, []))
    monkeypatch.setattr(flow, "write_silver_tables", lambda *_args: {})
    monkeypatch.setattr(flow, "write_gold_tables", lambda *_args: {})
    monkeypatch.setattr(flow, "write_registry", lambda *_args: {})
    flow.build_layers(None, tables, {}, [], "2026-11-16", Path("."), True)
    return observed


def test_non_silver_rows_are_released_after_bronze_write(monkeypatch) -> None:
    """Keep all source rows in Bronze, then narrow the live table mapping."""

    names = (*SILVER_TABLES, "activities", "mandate_remunerations", "participations")
    tables = {name: [] for name in names}

    observed = _exercise_build(monkeypatch, tables)

    assert observed["bronze"] == set(names)
    assert observed["silver"] == set(SILVER_TABLES)
    assert set(tables) == set(SILVER_TABLES)


def test_silver_input_rows_keep_their_identity(monkeypatch) -> None:
    """The memory reduction drops only tables unused by Silver and Gold."""

    tables = {name: [{"bronze_record_key": name}] for name in SILVER_TABLES}
    tables["mandate_remunerations"] = [{"bronze_record_key": "remuneration"}]
    row_ids = {name: id(rows) for name, rows in tables.items() if name in SILVER_TABLES}

    observed = _exercise_build(monkeypatch, tables)

    assert observed["silver_rows"] == row_ids
    assert "mandate_remunerations" in observed["bronze"]
    assert "mandate_remunerations" not in tables


def test_non_silver_records_reach_bronze_before_release(monkeypatch) -> None:
    """The full Bronze source table is written before it leaves memory."""

    rows = [{"bronze_record_key": "activity-row"}]
    tables = {name: [] for name in SILVER_TABLES}
    tables["activities"] = rows

    observed = _exercise_build(monkeypatch, tables)

    assert observed["bronze_rows"]["activities"] == id(rows)
    assert "activities" in observed["bronze"]
    assert "activities" not in tables
