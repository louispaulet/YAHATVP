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


__all__ = ["TABLE_COLUMNS", "all_table_names", "required_columns"]
