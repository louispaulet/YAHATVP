"""Fake BigQuery client primitives shared by loader tests."""

from __future__ import annotations

from google.api_core.exceptions import NotFound
from google.cloud import bigquery


class FakeJob:
    def result(self) -> None:
        return None


class FakeField:
    def __init__(self, name: str, field_type: str = "STRING", mode: str = "NULLABLE") -> None:
        self.name = name
        self.field_type = field_type
        self.mode = mode


class FakeTable:
    def __init__(self, schema: list[FakeField]) -> None:
        self.schema = schema


class FakeBigQueryClient:
    """Capture load, schema-evolution, partition-delete, and insert calls."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []
        self.tables: dict[str, FakeTable] = {}

    @staticmethod
    def key(table_ref: object) -> str:
        return str(table_ref)

    def get_dataset(self, dataset_ref: object) -> object:
        self.calls.append(("get_dataset", dataset_ref))
        return dataset_ref

    def get_table(self, table_ref: object) -> FakeTable:
        key = self.key(table_ref)
        if key not in self.tables:
            raise NotFound("table missing")
        return self.tables[key]

    def load_table_from_uri(
        self, uri: str, destination: object, *, location: str, job_config: bigquery.LoadJobConfig
    ) -> FakeJob:
        self.calls.append(("load_uri", (uri, destination, location, job_config)))
        self.tables[self.key(destination)] = FakeTable(
            [
                FakeField("declaration_uuid"),
                FakeField("snapshot_date", "DATE"),
                FakeField("income_stream"),
            ]
        )
        return FakeJob()

    def load_table_from_file(
        self,
        source: object,
        destination: object,
        *,
        location: str,
        job_config: bigquery.LoadJobConfig,
    ) -> FakeJob:
        self.calls.append(("load_file", (destination, location, job_config)))
        return self.load_table_from_uri(
            "local", destination, location=location, job_config=job_config
        )

    def query(
        self, query: str, *, location: str, job_config: bigquery.QueryJobConfig | None = None
    ) -> FakeJob:
        self.calls.append(("query", (query, location, job_config)))
        if query.startswith("CREATE TABLE "):
            target = query.split("`", 2)[1]
            staging = next(
                (table for key, table in self.tables.items() if "_hatvp_staging_" in key),
                FakeTable([]),
            )
            self.tables[target] = FakeTable(list(staging.schema))
        elif query.startswith("ALTER TABLE "):
            target = query.split("`", 2)[1]
            field_name = query.split("`", 4)[3]
            self.tables[target].schema.append(FakeField(field_name))
        return FakeJob()

    def delete_table(self, table_ref: object, *, not_found_ok: bool) -> None:
        self.calls.append(("delete_table", (table_ref, not_found_ok)))
        self.tables.pop(self.key(table_ref), None)


def query_texts(client: FakeBigQueryClient) -> list[str]:
    """Return captured SQL statements in execution order."""

    return [call[1][0] for call in client.calls if call[0] == "query"]
