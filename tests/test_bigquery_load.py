from pathlib import Path

from google.cloud import bigquery

from hatvp.bigquery import CURATED_TABLES, load_parquet_tables
from tests.bigquery_support import FakeBigQueryClient, FakeField, FakeTable, query_texts


def test_loader_uses_curated_tables_partitioning_and_replace_order(tmp_path: Path) -> None:
    table_files = {
        table_name: tmp_path / f"{table_name}.parquet"
        for table_name in (*CURATED_TABLES, "activities")
    }
    for path in table_files.values():
        path.write_bytes(b"fixture")
    gcs_uris = {
        table_name: f"gs://bucket/hatvp/silver/{table_name}/data.parquet"
        for table_name in table_files
    }
    client = FakeBigQueryClient()

    load_parquet_tables(
        project="fixture-project",
        dataset="hatvp",
        table_files=table_files,
        snapshot_date="2026-08-17",
        gcs_uris=gcs_uris,
        client=client,
        location="europe-west1",
    )

    load_calls = [call for call in client.calls if call[0] == "load_uri"]
    assert [call[1][0].split("/silver/")[1].split("/")[0] for call in load_calls] == list(
        CURATED_TABLES
    )
    assert all(
        call[1][3].write_disposition == bigquery.WriteDisposition.WRITE_TRUNCATE
        for call in load_calls
    )
    assert all(call[1][1] == "europe-west1" for call in client.calls if call[0] == "query")
    for table_name in CURATED_TABLES:
        table_id = f"`fixture-project.hatvp.{table_name}`"
        assert any(
            f"CREATE TABLE {table_id} PARTITION BY snapshot_date" in query
            for query in query_texts(client)
        )
        assert any(
            f"DELETE FROM {table_id} WHERE snapshot_date = @snapshot_date" in query
            for query in query_texts(client)
        )
    assert len([call for call in client.calls if call[0] == "delete_table"]) == 4


def test_loader_evolves_existing_schema_and_inserts_by_column_name(tmp_path: Path) -> None:
    path = tmp_path / "incomes.parquet"
    path.write_bytes(b"fixture")
    client = FakeBigQueryClient()
    target_ref = bigquery.DatasetReference("fixture-project", "hatvp").table("incomes")
    client.tables[str(target_ref)] = FakeTable(
        [FakeField("declaration_uuid"), FakeField("snapshot_date", "DATE")]
    )

    load_parquet_tables(
        project="fixture-project",
        dataset="hatvp",
        table_files={"incomes": path},
        snapshot_date="2026-08-17",
        table_names=("incomes",),
        client=client,
    )

    queries = query_texts(client)
    assert any("ADD COLUMN IF NOT EXISTS `income_stream`" in query for query in queries)
    insert = next(query for query in queries if query.startswith("INSERT INTO"))
    assert "`declaration_uuid`, `snapshot_date`, `income_stream`" in insert
    assert "SELECT `declaration_uuid`, `snapshot_date`, `income_stream`" in insert


def test_loader_requires_precreated_dataset(tmp_path: Path) -> None:
    class MissingDatasetClient(FakeBigQueryClient):
        def get_dataset(self, dataset_ref: object) -> object:
            raise RuntimeError("dataset missing")

    files = {name: tmp_path / f"{name}.parquet" for name in CURATED_TABLES}
    for path in files.values():
        path.write_bytes(b"fixture")

    try:
        load_parquet_tables(
            project="fixture-project",
            dataset="hatvp",
            table_files=files,
            snapshot_date="2026-08-17",
            client=MissingDatasetClient(),
        )
    except RuntimeError as exc:
        assert str(exc) == "dataset missing"
    else:
        raise AssertionError("missing dataset should fail before loading tables")
