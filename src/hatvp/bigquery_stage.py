"""BigQuery staging and snapshot replacement primitives."""

from __future__ import annotations

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


def load_stage(
    client: Any, staging_ref: Any, path: Path, uri: str | None, location: str, config: Any
) -> None:
    """Load one local or GCS Parquet source into a truncated staging table."""

    if uri:
        job = client.load_table_from_uri(uri, staging_ref, location=location, job_config=config)
    else:
        with path.open("rb") as source:
            job = client.load_table_from_file(
                source, staging_ref, location=location, job_config=config
            )
    job.result()


def replace_snapshot(
    client: Any,
    dataset_ref: Any,
    name: str,
    snapshot: str,
    location: str,
    bigquery: Any,
    not_found: Any,
) -> None:
    """Merge staged columns and replace only one partition of a curated table."""

    target = dataset_ref.table(name)
    target_id = table_id(dataset_ref.project, dataset_ref.dataset_id, name)
    staging_ref = dataset_ref.table(staging_table_name(name))
    staging_id = table_id(dataset_ref.project, dataset_ref.dataset_id, staging_table_name(name))
    target_table = _ensure_target(client, target, target_id, staging_id, location, not_found)
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
    columns = [field.name for field in target_table.schema]
    staged = {field.name for field in staging_table.schema}
    expressions = [
        f"`{column}`"
        if column in staged
        else f"CAST(NULL AS {field_type_sql(existing[column])}) AS `{column}`"
        for column in columns
    ]
    config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("snapshot_date", "DATE", snapshot)]
    )
    client.query(delete_sql(target_id), job_config=config, location=location).result()
    client.query(
        insert_sql(target_id, staging_id, columns, expressions), location=location
    ).result()


def _ensure_target(
    client: Any,
    target: Any,
    target_id: str,
    staging_id: str,
    location: str,
    not_found: Any,
) -> Any:
    try:
        return client.get_table(target)
    except not_found:
        client.query(create_partitioned_sql(target_id, staging_id), location=location).result()
        return client.get_table(target)


__all__ = ["load_stage", "replace_snapshot"]
