"""Required columns and curated-table selection metadata."""

from __future__ import annotations

from collections.abc import Mapping

TABLE_COLUMNS: Mapping[str, list[str]] = {
    "liste": ["snapshot_date", "source_file"],
    "declarations": ["declaration_uuid", "snapshot_date", "source_file"],
    "people": ["declaration_uuid", "snapshot_date", "source_file"],
    "mandates": ["declaration_uuid", "snapshot_date", "source_section"],
    "mandate_remunerations": [
        "declaration_uuid",
        "snapshot_date",
        "source_section",
        "remuneration_year",
        "normalized_value",
    ],
    "activities": ["declaration_uuid", "snapshot_date", "source_section"],
    "participations": ["declaration_uuid", "snapshot_date", "source_section"],
    "incomes": [
        "declaration_uuid",
        "snapshot_date",
        "source_section",
        "income_stream",
        "normalized_value",
    ],
    "assets": ["declaration_uuid", "snapshot_date", "source_section", "normalized_value"],
    "liabilities": ["declaration_uuid", "snapshot_date", "source_section", "normalized_value"],
}


def required_columns(table_name: str) -> list[str]:
    """Return a copy so writers cannot mutate the shared contract."""

    return list(TABLE_COLUMNS.get(table_name, ()))


def all_table_names() -> tuple[str, ...]:
    """Return the deterministic table order used for artifact writing."""

    return tuple(TABLE_COLUMNS)


def has_table_contract(table_name: str) -> bool:
    """Return whether a normalized output table has a declared column contract."""

    return table_name in TABLE_COLUMNS


def validate_table_name(table_name: str) -> str:
    """Validate a table name before writing a Parquet artifact."""

    if not has_table_contract(table_name):
        raise KeyError(f"Unknown normalized table: {table_name}")
    return table_name


def columns_for(table_name: str) -> tuple[str, ...]:
    """Return an immutable view for adapters that pass column contracts around."""

    validate_table_name(table_name)
    return tuple(TABLE_COLUMNS[table_name])


def column_count(table_name: str) -> int:
    """Return the number of required columns in a normalized table contract."""

    return len(columns_for(table_name))


__all__ = [
    "TABLE_COLUMNS",
    "all_table_names",
    "columns_for",
    "has_table_contract",
    "required_columns",
    "validate_table_name",
]
