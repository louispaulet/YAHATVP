from pathlib import Path

from google.cloud import bigquery

from hatvp.bigquery import CURATED_TABLES, load_parquet_tables


class _FakeJob:
    def result(self) -> None:
        return None


class _FakeBigQueryClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def get_dataset(self, dataset_ref: object) -> object:
        self.calls.append(("get_dataset", dataset_ref))
        return dataset_ref

    def load_table_from_uri(
        self,
        uri: str,
        destination: object,
        *,
        location: str,
        job_config: bigquery.LoadJobConfig,
    ) -> _FakeJob:
        self.calls.append(("load_uri", (uri, destination, location, job_config)))
        return _FakeJob()

    def load_table_from_file(
        self,
        source: object,
        destination: object,
        *,
        location: str,
        job_config: bigquery.LoadJobConfig,
    ) -> _FakeJob:
        self.calls.append(("load_file", (destination, location, job_config)))
        return _FakeJob()

    def query(
        self,
        query: str,
        *,
        location: str,
        job_config: bigquery.QueryJobConfig | None = None,
    ) -> _FakeJob:
        self.calls.append(("query", (query, location, job_config)))
        return _FakeJob()

    def delete_table(self, table_ref: object, *, not_found_ok: bool) -> None:
        self.calls.append(("delete_table", (table_ref, not_found_ok)))


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
    client = _FakeBigQueryClient()

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
    assert not any("activities" in str(call) for call in load_calls)

    query_calls = [call[1][0] for call in client.calls if call[0] == "query"]
    assert all(call[1][1] == "europe-west1" for call in client.calls if call[0] == "query")
    for table_name in CURATED_TABLES:
        table_id = f"`fixture-project.hatvp.{table_name}`"
        assert any(
            f"CREATE TABLE IF NOT EXISTS {table_id} PARTITION BY snapshot_date" in query
            for query in query_calls
        )
        assert any(
            f"DELETE FROM {table_id} WHERE snapshot_date = @snapshot_date" in query
            for query in query_calls
        )
        assert any(f"INSERT INTO {table_id} SELECT *" in query for query in query_calls)

    deleted_staging = [call for call in client.calls if call[0] == "delete_table"]
    assert len(deleted_staging) == len(CURATED_TABLES)


def test_loader_requires_precreated_dataset(tmp_path: Path) -> None:
    class MissingDatasetClient(_FakeBigQueryClient):
        def get_dataset(self, dataset_ref: object) -> object:
            raise RuntimeError("dataset missing")

    files = {table_name: tmp_path / f"{table_name}.parquet" for table_name in CURATED_TABLES}
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
