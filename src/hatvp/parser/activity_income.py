"""Unified income rows sourced from recent professional activity remuneration."""

from __future__ import annotations

from typing import Any

from lxml import etree

from ..models import ParseContext, ParserConfig
from ..xml_support import child, item_groups, normalized_child_text
from .mandate_fields import mandate_item_fields, mandate_raw_record, remuneration_entries

DEFAULT_INCOME_ACTIVITY_SECTIONS = ("activProfCinqDerniereDto",)


def activity_income_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    """Return one unified income row for every annual professional-activity value."""

    uuid = normalized_child_text(element, "uuid")
    rows: list[dict[str, Any]] = []
    sections = config.sections.get("income_activities", DEFAULT_INCOME_ACTIVITY_SECTIONS)
    for section_name in sections:
        for item_index, item in enumerate(item_groups(child(element, section_name))):
            entries = remuneration_entries(item)
            if not entries:
                continue
            fields = mandate_item_fields(item)
            record = mandate_raw_record(item, entries)
            rows.extend(
                _rows_for_item(uuid, context, section_name, item_index, fields, entries, record)
            )
    return rows


def _rows_for_item(
    uuid: str | None,
    context: ParseContext,
    section_name: str,
    item_index: int,
    fields: dict[str, Any],
    entries: list[dict[str, Any]],
    record: str,
) -> list[dict[str, Any]]:
    return [
        {
            "declaration_uuid": uuid,
            "snapshot_date": context.snapshot_date,
            "source_section": section_name,
            "income_stream": "activity_remuneration",
            "source_item_index": item_index,
            "income_category_index": None,
            "income_year": entry["remuneration_year_raw"],
            "income_type": fields["description"] or "activity_remuneration",
            "raw_value": entry["raw_value"],
            "normalized_value": entry["normalized_value"],
            "spouse_raw_value": None,
            "spouse_normalized_value": None,
            "quality_status": "OK",
            "quality_reason": None,
            "raw_record_json": record,
            "remuneration_index": index,
        }
        for index, entry in enumerate(entries)
    ]


def is_activity_income_row(row: dict[str, Any]) -> bool:
    """Identify unified income rows sourced from professional activity."""

    return row.get("income_stream") == "activity_remuneration"


def activity_income_years(rows: list[dict[str, Any]]) -> list[str | None]:
    """Return professional-activity source years in normalized row order."""

    return [row.get("income_year") for row in rows if is_activity_income_row(row)]


__all__ = ["activity_income_rows", "activity_income_years", "is_activity_income_row"]
