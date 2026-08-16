from __future__ import annotations

from pathlib import Path


def load_parquet_tables(
    *,
    project: str,
    dataset: str,
    table_files: dict[str, Path],
    snapshot_date: str,
    gcs_uris: dict[str, str] | None = None,
) -> None:
    """Load Parquet tables into BigQuery idempotently for one snapshot.

    GCS URIs are preferred in production because the Cloud Run job should not need
    to hold large Parquet files in memory. Local paths are retained for a future
    emulator/test adapter and are not used by the default GCS pipeline.
    """

    from google.cloud import bigquery

    client = bigquery.Client(project=project)
    dataset_ref = bigquery.DatasetReference(project, dataset)
    client.create_dataset(bigquery.Dataset(dataset_ref), exists_ok=True)

    for table_name, parquet_path in table_files.items():
        staging_ref = dataset_ref.table(f"_hatvp_staging_{table_name}")
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            autodetect=True,
        )
        if gcs_uris and table_name in gcs_uris:
            load_job = client.load_table_from_uri(
                gcs_uris[table_name], staging_ref, job_config=job_config
            )
        else:
            with parquet_path.open("rb") as source:
                load_job = client.load_table_from_file(source, staging_ref, job_config=job_config)
        load_job.result()

        table_id = f"`{project}.{dataset}.{table_name}`"
        staging_id = f"`{project}.{dataset}._hatvp_staging_{table_name}`"
        client.query(
            f"CREATE TABLE IF NOT EXISTS {table_id} PARTITION BY snapshot_date "
            f"AS SELECT * FROM {staging_id} WHERE FALSE"
        ).result()
        delete_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("snapshot_date", "DATE", snapshot_date)]
        )
        client.query(
            f"DELETE FROM {table_id} WHERE snapshot_date = @snapshot_date",
            job_config=delete_config,
        ).result()
        client.query(f"INSERT INTO {table_id} SELECT * FROM {staging_id}").result()
        client.delete_table(staging_ref, not_found_ok=True)
