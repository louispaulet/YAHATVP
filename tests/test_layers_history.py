"""Historical loading retains legacy Silver data beside newer Bronze data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hatvp.layers.history import history_row_count, history_snapshot_dates, load_bronze_history
from hatvp.storage import LocalArtifactStore
from hatvp.tables import write_table


def income_row(key: str, snapshot: str, value: float) -> dict[str, Any]:
    """Build the minimum source-shaped row accepted by the income schema."""

    return {
        "bronze_record_key": key,
        "declaration_uuid": key,
        "snapshot_date": snapshot,
        "source_section": "revenuMandatDto",
        "income_stream": "revenu_mandat",
        "income_year": "2024",
        "raw_value": str(value),
        "normalized_value": value,
    }


def write_partition(store: LocalArtifactStore, root: Path, layer: str, row: dict[str, Any]) -> None:
    """Write one fixture partition using the same Parquet contract as production."""

    source = root / f"{layer}-{row['bronze_record_key']}.parquet"
    write_table([row], "incomes", source)
    store.put_file(f"{layer}/incomes/snapshot_date={row['snapshot_date']}/data.parquet", source)


def test_mixed_bronze_and_legacy_silver_partitions_are_both_loaded(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "store", "hatvp")
    legacy = income_row("legacy", "2025-01-01", 10.0)
    current = income_row("current", "2026-01-01", 20.0)

    write_partition(store, tmp_path, "silver", legacy)
    write_partition(store, tmp_path, "bronze", current)

    history = load_bronze_history(store)

    assert {row["bronze_record_key"] for row in history["incomes"]} == {"legacy", "current"}
    assert history_snapshot_dates(history) == ("2025-01-01", "2026-01-01")
    assert history_row_count(history) == 2


def test_non_parquet_history_objects_are_ignored(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "store", "hatvp")
    store.put_bytes("silver/incomes/snapshot_date=2025-01-01/README.txt", b"not data")

    history = load_bronze_history(store)

    assert history == {name: [] for name in ("declarations", "people", "incomes", "assets")}


def test_history_snapshot_dates_skips_rows_without_a_snapshot() -> None:
    """Exclude records that cannot contribute a snapshot partition."""

    history = {"incomes": [{"bronze_record_key": "missing"}, {"snapshot_date": "2026-01-01"}]}

    assert history_snapshot_dates(history) == ("2026-01-01",)
    assert history_row_count(history) == 2


def test_history_snapshot_dates_uses_source_snapshot_fallback() -> None:
    history = {"incomes": [{"source_snapshot_date": "2024-01-01"}]}

    assert history_snapshot_dates(history) == ("2024-01-01",)
