from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

CURATED_TABLES = ("declarations", "people", "incomes", "assets")


def load_parquet_tables(
    *,
    project: str,
    dataset: str,
    table_files: dict[str, Path],
    snapshot_date: str,
    gcs_uris: dict[str, str] | None = None,
    table_names: Sequence[str] = CURATED_TABLES,
    location: str = "europe-west1",
    client: Any | None = None,
) -> None:
    """Load Parquet tables into BigQuery idempotently for one snapshot.

    GCS URIs are preferred in production because the Cloud Run job should not need
    to hold large Parquet files in memory. Local paths are retained for a future
    emulator/test adapter and are not used by the default GCS pipeline.
    """

    from google.api_core.exceptions import NotFound
    from google.cloud import bigquery

    selected_tables = tuple(table_names)
    missing_tables = [table_name for table_name in selected_tables if table_name not in table_files]
    if missing_tables:
        raise ValueError(f"Missing required BigQuery table files: {', '.join(missing_tables)}")

    client = client or bigquery.Client(project=project, location=location)
    dataset_ref = bigquery.DatasetReference(project, dataset)
    client.get_dataset(dataset_ref)

    for table_name in selected_tables:
        parquet_path = table_files[table_name]
        staging_ref = dataset_ref.table(f"_hatvp_staging_{table_name}")
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            autodetect=True,
        )
        try:
            if gcs_uris and table_name in gcs_uris:
                load_job = client.load_table_from_uri(
                    gcs_uris[table_name],
                    staging_ref,
                    location=location,
                    job_config=job_config,
                )
            else:
                with parquet_path.open("rb") as source:
                    load_job = client.load_table_from_file(
                        source,
                        staging_ref,
                        location=location,
                        job_config=job_config,
                    )
            load_job.result()

            table_id = f"`{project}.{dataset}.{table_name}`"
            staging_id = f"`{project}.{dataset}._hatvp_staging_{table_name}`"
            target_ref = dataset_ref.table(table_name)
            try:
                target_table = client.get_table(target_ref)
            except NotFound:
                client.query(
                    f"CREATE TABLE {table_id} PARTITION BY snapshot_date "
                    f"AS SELECT * FROM {staging_id} WHERE FALSE",
                    location=location,
                ).result()
                target_table = client.get_table(target_ref)

            staging_table = client.get_table(staging_ref)
            target_fields = {field.name: field for field in target_table.schema}

            def field_type_sql(field: Any) -> str:
                field_type = field.field_type
                return f"ARRAY<{field_type}>" if field.mode == "REPEATED" else field_type

            for field in staging_table.schema:
                if field.name in target_fields:
                    continue
                client.query(
                    f"ALTER TABLE {table_id} ADD COLUMN IF NOT EXISTS `{field.name}` "
                    f"{field_type_sql(field)}",
                    location=location,
                ).result()
            target_table = client.get_table(target_ref)
            staging_fields = {field.name for field in staging_table.schema}
            insert_columns = [field.name for field in target_table.schema]
            select_expressions = [
                f"`{field_name}`"
                if field_name in staging_fields
                else (
                    f"CAST(NULL AS {field_type_sql(target_fields[field_name])}) AS `{field_name}`"
                )
                for field_name in insert_columns
            ]
            delete_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("snapshot_date", "DATE", snapshot_date)
                ]
            )
            client.query(
                f"DELETE FROM {table_id} WHERE snapshot_date = @snapshot_date",
                job_config=delete_config,
                location=location,
            ).result()
            client.query(
                f"INSERT INTO {table_id} ({', '.join(f'`{name}`' for name in insert_columns)}) "
                f"SELECT {', '.join(select_expressions)} FROM {staging_id}",
                location=location,
            ).result()
        finally:
            client.delete_table(staging_ref, not_found_ok=True)
