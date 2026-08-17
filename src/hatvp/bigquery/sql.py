"""Small SQL builders keeping BigQuery loader statements explicit."""

from __future__ import annotations

from typing import Any


def field_type_sql(field: Any) -> str:
    """Translate a BigQuery schema field into an ALTER/CAST type expression."""

    return f"ARRAY<{field.field_type}>" if field.mode == "REPEATED" else field.field_type


def table_id(project: str, dataset: str, table: str) -> str:
    return f"`{project}.{dataset}.{table}`"


def quote_columns(columns: list[str]) -> str:
    """Quote column names for explicit BigQuery INSERT projections."""

    return ", ".join(f"`{column}`" for column in columns)


def staging_table_name(table: str) -> str:
    return f"_hatvp_staging_{table}"


def insert_sql(target: str, staging: str, columns: list[str], expressions: list[str]) -> str:
    return (
        f"INSERT INTO {target} ({quote_columns(columns)}) "
        f"SELECT {', '.join(expressions)} FROM {staging}"
    )


def delete_sql(target: str) -> str:
    return f"DELETE FROM {target} WHERE snapshot_date = @snapshot_date"


def create_partitioned_sql(target: str, staging: str) -> str:
    return (
        f"CREATE TABLE {target} PARTITION BY snapshot_date AS SELECT * FROM {staging} WHERE FALSE"
    )


def snapshot_parameter_name() -> str:
    """Return the named parameter shared by delete statements and query jobs."""

    return "snapshot_date"


def snapshot_filter_sql(target: str) -> str:
    """Build the explicit partition predicate used by replacement queries."""

    return f"{target}.snapshot_date = @{snapshot_parameter_name()}"


def select_sql(columns: list[str], source: str) -> str:
    """Build a quoted SELECT projection for schema-evolution tests."""

    return f"SELECT {quote_columns(columns)} FROM {source}"


__all__ = [
    "create_partitioned_sql",
    "delete_sql",
    "field_type_sql",
    "insert_sql",
    "quote_columns",
    "select_sql",
    "staging_table_name",
    "snapshot_filter_sql",
    "snapshot_parameter_name",
    "table_id",
]
