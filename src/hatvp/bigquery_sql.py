"""Small SQL builders keeping BigQuery loader statements explicit."""

from __future__ import annotations

from typing import Any


def field_type_sql(field: Any) -> str:
    """Translate a BigQuery schema field into an ALTER/CAST type expression."""

    return f"ARRAY<{field.field_type}>" if field.mode == "REPEATED" else field.field_type


def table_id(project: str, dataset: str, table: str) -> str:
    return f"`{project}.{dataset}.{table}`"


def staging_table_name(table: str) -> str:
    return f"_hatvp_staging_{table}"


def insert_sql(target: str, staging: str, columns: list[str], expressions: list[str]) -> str:
    names = ", ".join(f"`{column}`" for column in columns)
    return f"INSERT INTO {target} ({names}) SELECT {', '.join(expressions)} FROM {staging}"


def delete_sql(target: str) -> str:
    return f"DELETE FROM {target} WHERE snapshot_date = @snapshot_date"


def create_partitioned_sql(target: str, staging: str) -> str:
    return (
        f"CREATE TABLE {target} PARTITION BY snapshot_date AS SELECT * FROM {staging} WHERE FALSE"
    )


__all__ = [
    "create_partitioned_sql",
    "delete_sql",
    "field_type_sql",
    "insert_sql",
    "staging_table_name",
    "table_id",
]
