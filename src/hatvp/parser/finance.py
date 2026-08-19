"""Asset and liability row parsers driven by YAML field candidates."""

from __future__ import annotations

import re
from typing import Any

from lxml import etree

from ..models import ParseContext, ParserConfig
from ..normalize import normalize_text, parse_date, parse_french_number, parse_year
from ..xml_support import (
    child,
    first_value,
    flatten_leaf_values,
    item_groups,
    normalized_child_text,
    raw_record,
)

ASSET_EVENT_FIELDS = (
    "dateAcquisition dateAchat anneeAcquisition dateSouscription dateDetention".split()
)


def _asset_event(fields: dict[str, Any]) -> tuple[Any, Any, Any, Any]:
    for source in ASSET_EVENT_FIELDS:
        raw = normalize_text(fields.get(source))
        if raw:
            if re.fullmatch(r"\d{4}", raw):
                precision = "year"
            elif re.fullmatch(r"(?:\d{2}/\d{4}|\d{4}-\d{2})", raw):
                precision = "month"
            else:
                precision = "day" if parse_date(raw) else "unknown"
            return raw, parse_date(raw) if precision == "day" else None, precision, source
    return None, None, None, None


def asset_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    uuid = normalized_child_text(element, "uuid")
    sections = config.sections["assets"]
    values = config.field_candidates["asset_value"]
    names = config.field_candidates["asset_name"]
    rows: list[dict[str, Any]] = []
    for section_name in sections:
        for index, item in enumerate(item_groups(child(element, section_name))):
            fields = flatten_leaf_values(item)
            raw_value = first_value(fields, *values)
            acquisition_raw, event_date, event_precision, event_source = _asset_event(fields)
            rows.append(
                {
                    "declaration_uuid": uuid,
                    "snapshot_date": context.snapshot_date,
                    "source_section": section_name,
                    "source_item_index": index,
                    "asset_name": normalize_text(first_value(fields, *names)),
                    "raw_value": raw_value,
                    "normalized_value": parse_french_number(raw_value),
                    "asset_acquisition_year_raw": acquisition_raw,
                    "asset_acquisition_year": parse_year(acquisition_raw),
                    "asset_event_date": event_date,
                    "asset_event_precision": event_precision,
                    "asset_event_source_field": event_source,
                    "quality_status": "OK",
                    "quality_reason": None,
                    "raw_record_json": raw_record(fields),
                }
            )
    return rows


def liability_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    uuid = normalized_child_text(element, "uuid")
    section = config.sections["liabilities"]
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(item_groups(child(element, section))):
        fields = flatten_leaf_values(item)
        raw_value = first_value(fields, *config.field_candidates["liability_value"])
        rows.append(
            {
                "declaration_uuid": uuid,
                "snapshot_date": context.snapshot_date,
                "source_section": section,
                "source_item_index": index,
                "description": normalize_text(
                    first_value(fields, *config.field_candidates["liability_description"])
                ),
                "raw_value": raw_value,
                "normalized_value": parse_french_number(raw_value),
                "raw_record_json": raw_record(fields),
            }
        )
    return rows
