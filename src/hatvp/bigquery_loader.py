"""Idempotent BigQuery staging and snapshot replacement implementation."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .bigquery_sql import (
    create_partitioned_sql,
    delete_sql,
    field_type_sql,
    insert_sql,
    staging_table_name,
    table_id,
)


def load_parquet_tables(
    *,
    project: str,
    dataset: str,
    table_files: dict[str, Path],
    snapshot_date: str,
    gcs_uris: dict[str, str] | None = None,
    table_names: Sequence[str] = ("declarations", "people", "incomes", "assets"),
    location: str = "europe-west1",
    client: Any | None = None,
) -> None:
    """Load selected Parquet tables and replace only the requested snapshot."""

    from google.api_core.exceptions import NotFound
    from google.cloud import bigquery

    selected = tuple(table_names)
    missing = [name for name in selected if name not in table_files]
    if missing:
        raise ValueError(f"Missing required BigQuery table files: {', '.join(missing)}")
    client = client or bigquery.Client(project=project, location=location)
    dataset_ref = bigquery.DatasetReference(project, dataset)
    client.get_dataset(dataset_ref)
    for name in selected:
        staging_ref = dataset_ref.table(staging_table_name(name))
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            autodetect=True,
        )
        try:
            _load_stage(
                client,
                staging_ref,
                table_files[name],
                gcs_uris.get(name) if gcs_uris else None,
                location,
                job_config,
            )
            _replace_snapshot(
                client, dataset_ref, name, snapshot_date, location, bigquery, NotFound
            )
        finally:
            client.delete_table(staging_ref, not_found_ok=True)


def _load_stage(
    client: Any, staging_ref: Any, path: Path, uri: str | None, location: str, config: Any
) -> None:
    if uri:
        job = client.load_table_from_uri(uri, staging_ref, location=location, job_config=config)
    else:
        with path.open("rb") as source:
            job = client.load_table_from_file(
                source, staging_ref, location=location, job_config=config
            )
    job.result()


def _replace_snapshot(
    client: Any,
    dataset_ref: Any,
    name: str,
    snapshot: str,
    location: str,
    bigquery: Any,
    not_found: Any,
) -> None:
    target = dataset_ref.table(name)
    target_id = table_id(dataset_ref.project, dataset_ref.dataset_id, name)
    staging_ref = dataset_ref.table(staging_table_name(name))
    staging_id = table_id(dataset_ref.project, dataset_ref.dataset_id, staging_table_name(name))
    try:
        target_table = client.get_table(target)
    except not_found:
        client.query(create_partitioned_sql(target_id, staging_id), location=location).result()
        target_table = client.get_table(target)
    staging_table = client.get_table(staging_ref)
    existing = {field.name: field for field in target_table.schema}
    for field in staging_table.schema:
        if field.name not in existing:
            client.query(
                f"ALTER TABLE {target_id} ADD COLUMN IF NOT EXISTS `{field.name}` "
                f"{field_type_sql(field)}",
                location=location,
            ).result()
    target_table = client.get_table(target)
    staged = {field.name for field in staging_table.schema}
    columns = [field.name for field in target_table.schema]
    expressions = [
        f"`{name}`"
        if name in staged
        else f"CAST(NULL AS {field_type_sql(existing[name])}) AS `{name}`"
        for name in columns
    ]
    config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("snapshot_date", "DATE", snapshot)]
    )
    client.query(delete_sql(target_id), job_config=config, location=location).result()
    client.query(
        insert_sql(target_id, staging_id, columns, expressions), location=location
    ).result()
