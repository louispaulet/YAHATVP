"""Identity and value matching helpers for quality-triage evidence."""

from __future__ import annotations

from typing import Any


def normal_name(value: Any) -> str:
    """Normalize human names for evidence matching without changing source rows."""

    return " ".join(str(value or "").split()).casefold()


def name_rows(rows: list[dict[str, Any]], raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Select source or persisted people with the same normalized name."""

    first = normal_name(raw.get("prenom"))
    last = normal_name(raw.get("nom"))
    return [
        row
        for row in rows
        if normal_name(row.get("prenom")) == first and normal_name(row.get("nom")) == last
    ]


def asset_key(row: dict[str, Any]) -> tuple[Any, ...]:
    """Return the stable source position key used for asset reconciliation."""

    return row.get("declaration_uuid"), row.get("source_section"), row.get("source_item_index")


def assets_match(
    source: list[dict[str, Any]], persisted: list[dict[str, Any]], raw: dict[str, Any]
) -> bool:
    """Check source and persisted asset values while retaining outlier fields."""

    return any(
        same_asset_values(row, raw) and any(same_asset_values(saved, raw) for saved in persisted)
        for row in source
    )


def same_asset_values(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """Compare the value fields that define a normalized asset observation."""

    return all(
        left.get(field) == right.get(field)
        for field in ("raw_value", "normalized_value", "asset_name")
    )


def asset_rows(
    rows: list[dict[str, Any]], declaration_uuid: str | None, raw: dict[str, Any]
) -> list[dict[str, Any]]:
    """Select assets at the same declaration and source-item position."""

    key = (
        declaration_uuid,
        raw.get("source_section"),
        raw.get("source_item_index"),
    )
    return [row for row in rows if asset_key(row) == key]


__all__ = [
    "asset_key",
    "asset_rows",
    "assets_match",
    "name_rows",
    "normal_name",
    "same_asset_values",
]
