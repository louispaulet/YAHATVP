"""Direct tests for BigQuery selection, SQL, and curated schema boundaries."""

from pathlib import Path

import pytest

from hatvp.bigquery import curated_table_names, validate_table_files, validate_table_selection
from hatvp.bigquery_loader import curated_load_defaults, staging_name
from hatvp.bigquery_sql import (
    create_partitioned_sql,
    delete_sql,
    field_type_sql,
    insert_sql,
    quote_columns,
    select_sql,
    snapshot_filter_sql,
    snapshot_parameter_name,
    table_id,
)
from tests.bigquery_support import FakeField


def test_curated_selection_rejects_non_curated_tables() -> None:
    assert curated_table_names() == ("declarations", "people", "incomes", "assets")
    assert validate_table_selection(["incomes"]) == ("incomes",)
    with pytest.raises(ValueError, match="Unsupported"):
        validate_table_selection(["activities"])


def test_file_selection_reports_missing_curated_outputs(tmp_path: Path) -> None:
    path = tmp_path / "incomes.parquet"
    path.write_bytes(b"fixture")

    assert validate_table_files({"incomes": path}, ("incomes",)) == ("incomes",)
    with pytest.raises(ValueError, match="Missing required"):
        validate_table_files({}, ("incomes",))


def test_sql_builders_keep_partition_and_projection_semantics_explicit() -> None:
    target = table_id("project", "dataset", "incomes")
    staging = table_id("project", "dataset", "_hatvp_staging_incomes")

    assert quote_columns(["id", "snapshot_date"]) == "`id`, `snapshot_date`"
    assert insert_sql(target, staging, ["id"], ["`id`"]).startswith("INSERT INTO")
    assert delete_sql(target).endswith("snapshot_date = @snapshot_date")
    assert create_partitioned_sql(target, staging).startswith("CREATE TABLE")
    assert select_sql(["id"], staging) == f"SELECT `id` FROM {staging}"
    assert snapshot_filter_sql(target).endswith("@snapshot_date")
    assert snapshot_parameter_name() == "snapshot_date"


def test_schema_field_and_staging_names_are_compatible() -> None:
    repeated = FakeField("labels", "STRING", "REPEATED")

    assert field_type_sql(repeated) == "ARRAY<STRING>"
    assert field_type_sql(FakeField("name")) == "STRING"
    assert staging_name("assets") == "_hatvp_staging_assets"
    assert curated_load_defaults() == curated_table_names()


def test_selection_preserves_requested_order_for_partial_reloads(tmp_path: Path) -> None:
    files = {}
    for name in ("assets", "incomes"):
        files[name] = tmp_path / f"{name}.parquet"
        files[name].write_bytes(b"fixture")

    selected = validate_table_files(files, ("assets", "incomes"))

    assert selected == ("assets", "incomes")


def test_sql_builders_quote_empty_and_multiple_columns() -> None:
    assert quote_columns([]) == ""
    assert select_sql(["id", "name"], "source") == "SELECT `id`, `name` FROM source"
