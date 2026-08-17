from pathlib import Path

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from hatvp.bigquery import CURATED_TABLES, load_parquet_tables


class _FakeJob:
    def result(self) -> None:
        return None


class _FakeField:
    def __init__(self, name: str, field_type: str = "STRING", mode: str = "NULLABLE") -> None:
        self.name = name
        self.field_type = field_type
        self.mode = mode


class _FakeTable:
    def __init__(self, schema: list[_FakeField]) -> None:
        self.schema = schema


class _FakeBigQueryClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []
        self.tables: dict[str, _FakeTable] = {}

    @staticmethod
    def _key(table_ref: object) -> str:
        return str(table_ref)

    def get_dataset(self, dataset_ref: object) -> object:
        self.calls.append(("get_dataset", dataset_ref))
        return dataset_ref

    def get_table(self, table_ref: object) -> _FakeTable:
        key = self._key(table_ref)
        if key not in self.tables:
            raise NotFound("table missing")
        return self.tables[key]

    def load_table_from_uri(
        self,
        uri: str,
        destination: object,
        *,
        location: str,
        job_config: bigquery.LoadJobConfig,
    ) -> _FakeJob:
        self.calls.append(("load_uri", (uri, destination, location, job_config)))
        self.tables[self._key(destination)] = _FakeTable(
            [
                _FakeField("declaration_uuid"),
                _FakeField("snapshot_date", "DATE"),
                _FakeField("income_stream"),
            ]
        )
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
        self.tables[self._key(destination)] = _FakeTable(
            [
                _FakeField("declaration_uuid"),
                _FakeField("snapshot_date", "DATE"),
                _FakeField("income_stream"),
            ]
        )
        return _FakeJob()

    def query(
        self,
        query: str,
        *,
        location: str,
        job_config: bigquery.QueryJobConfig | None = None,
    ) -> _FakeJob:
        self.calls.append(("query", (query, location, job_config)))
        if query.startswith("CREATE TABLE "):
            target = query.split("`", 2)[1]
            staging = next(
                (table for key, table in self.tables.items() if "_hatvp_staging_" in key),
                _FakeTable([]),
            )
            self.tables[target] = _FakeTable(list(staging.schema))
        elif query.startswith("ALTER TABLE "):
            target = query.split("`", 2)[1]
            field_name = query.split("`", 4)[3]
            self.tables[target].schema.append(_FakeField(field_name))
        return _FakeJob()

    def delete_table(self, table_ref: object, *, not_found_ok: bool) -> None:
        self.calls.append(("delete_table", (table_ref, not_found_ok)))
        self.tables.pop(self._key(table_ref), None)


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
            f"CREATE TABLE {table_id} PARTITION BY snapshot_date" in query for query in query_calls
        )
        assert any(
            f"DELETE FROM {table_id} WHERE snapshot_date = @snapshot_date" in query
            for query in query_calls
        )
        assert any(
            f"INSERT INTO {table_id} (`declaration_uuid`, `snapshot_date`, `income_stream`)"
            in query
            for query in query_calls
        )

    deleted_staging = [call for call in client.calls if call[0] == "delete_table"]
    assert len(deleted_staging) == len(CURATED_TABLES)


def test_loader_evolves_existing_schema_and_inserts_by_column_name(tmp_path: Path) -> None:
    table_name = "incomes"
    table_file = tmp_path / f"{table_name}.parquet"
    table_file.write_bytes(b"fixture")
    client = _FakeBigQueryClient()
    target_ref = bigquery.DatasetReference("fixture-project", "hatvp").table(table_name)
    client.tables[str(target_ref)] = _FakeTable(
        [
            _FakeField("declaration_uuid"),
            _FakeField("snapshot_date", "DATE"),
        ]
    )

    load_parquet_tables(
        project="fixture-project",
        dataset="hatvp",
        table_files={table_name: table_file},
        snapshot_date="2026-08-17",
        table_names=(table_name,),
        client=client,
    )

    query_calls = [call[1][0] for call in client.calls if call[0] == "query"]
    assert any(
        "ALTER TABLE `fixture-project.hatvp.incomes` ADD COLUMN IF NOT EXISTS `income_stream`"
        in query
        for query in query_calls
    )
    insert_query = next(query for query in query_calls if query.startswith("INSERT INTO"))
    assert (
        "INSERT INTO `fixture-project.hatvp.incomes` ("
        "`declaration_uuid`, `snapshot_date`, `income_stream`)" in insert_query
    )
    assert "SELECT `declaration_uuid`, `snapshot_date`, `income_stream`" in insert_query


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
