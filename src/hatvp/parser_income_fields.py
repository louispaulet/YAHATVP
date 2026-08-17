"""Row-shaping helpers for declared income categories."""

from __future__ import annotations

from typing import Any

from .models import ParseContext
from .normalize import normalize_text, parse_french_number


def income_row(
    uuid: str | None,
    context: ParseContext,
    item_index: int,
    category_index: int | None,
    year: str | None,
    values: dict[str, Any],
    raw_value: Any,
    spouse_raw: Any,
    source_record: str,
    income_type: str | None = None,
) -> dict[str, Any]:
    return {
        "declaration_uuid": uuid,
        "snapshot_date": context.snapshot_date,
        "source_section": "revenuMandatDto",
        "income_stream": "revenu_mandat",
        "source_item_index": item_index,
        "income_category_index": category_index,
        "income_year": year,
        "income_type": income_type or normalize_text(values.get("typeRevenu")),
        "raw_value": raw_value,
        "normalized_value": parse_french_number(raw_value),
        "spouse_raw_value": spouse_raw,
        "spouse_normalized_value": parse_french_number(spouse_raw),
        "quality_status": "OK",
        "quality_reason": None,
        "raw_record_json": source_record,
    }


def is_populated(raw_value: Any, spouse_raw: Any) -> bool:
    return raw_value is not None or spouse_raw is not None


def income_value_pair(row: dict[str, Any]) -> tuple[Any, Any]:
    """Return the declared and spouse values from a normalized income row."""

    return row.get("raw_value"), row.get("spouse_raw_value")


def income_numeric_pair(row: dict[str, Any]) -> tuple[float | None, float | None]:
    """Return both normalized numeric values for quality and fixture assertions."""

    return row.get("normalized_value"), row.get("spouse_normalized_value")


def income_has_numeric_value(row: dict[str, Any]) -> bool:
    """Return whether either person has a successfully parsed numeric amount."""

    return any(value is not None for value in income_numeric_pair(row))


__all__ = [
    "income_has_numeric_value",
    "income_numeric_pair",
    "income_row",
    "income_value_pair",
    "is_populated",
]
