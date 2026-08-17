"""Unified income rows sourced from annual elected-mandate remuneration."""

from __future__ import annotations

from typing import Any

from lxml import etree

from .models import ParseContext, ParserConfig
from .parser_mandate_fields import mandate_item_fields, mandate_raw_record, remuneration_entries
from .xml_support import child, item_groups, normalized_child_text


def mandate_income_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    uuid = normalized_child_text(element, "uuid")
    section = child(element, config.sections["mandate"])
    rows: list[dict[str, Any]] = []
    for item_index, item in enumerate(item_groups(section)):
        fields = mandate_item_fields(item)
        entries = remuneration_entries(item)
        record = mandate_raw_record(item, entries)
        rows.extend(_rows_for_item(uuid, context, item_index, fields, entries, record))
    return rows


def _rows_for_item(
    uuid: str | None,
    context: ParseContext,
    item_index: int,
    fields: dict[str, Any],
    entries: list[dict[str, Any]],
    record: str,
) -> list[dict[str, Any]]:
    return [
        {
            "declaration_uuid": uuid,
            "snapshot_date": context.snapshot_date,
            "source_section": "mandatElectifDto",
            "income_stream": "mandate_remuneration",
            "source_item_index": item_index,
            "income_category_index": None,
            "income_year": entry["remuneration_year_raw"],
            "income_type": fields["description"]
            or entry["remuneration_basis"]
            or "mandate_remuneration",
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


__all__ = ["mandate_income_rows"]
