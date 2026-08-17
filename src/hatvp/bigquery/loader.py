"""Idempotent BigQuery staging and snapshot replacement implementation."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .sql import staging_table_name
from .stage import load_stage, replace_snapshot


def validate_table_files(
    table_files: dict[str, Path], table_names: Sequence[str]
) -> tuple[str, ...]:
    """Validate the selected load set before creating any staging table."""

    selected = tuple(table_names)
    missing = [name for name in selected if name not in table_files]
    if missing:
        raise ValueError(f"Missing required BigQuery table files: {', '.join(missing)}")
    return selected


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

    selected = validate_table_files(table_files, table_names)
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
            load_stage(
                client,
                staging_ref,
                table_files[name],
                gcs_uris.get(name) if gcs_uris else None,
                location,
                job_config,
            )
            replace_snapshot(client, dataset_ref, name, snapshot_date, location, bigquery, NotFound)
        finally:
            client.delete_table(staging_ref, not_found_ok=True)


def curated_load_defaults() -> tuple[str, ...]:
    """Document the default table order independently of the façade module."""

    return ("declarations", "people", "incomes", "assets")


def staging_name(table_name: str) -> str:
    """Return the transient table name used during one idempotent load."""

    return staging_table_name(table_name)


__all__ = ["curated_load_defaults", "load_parquet_tables", "staging_name", "validate_table_files"]
