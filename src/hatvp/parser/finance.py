"""Asset and liability row parsers driven by YAML field candidates."""

from __future__ import annotations

from typing import Any

from lxml import etree

from ..models import ParseContext, ParserConfig
from ..normalize import normalize_text, parse_french_number, parse_year
from ..xml_support import (
    child,
    first_value,
    flatten_leaf_values,
    item_groups,
    normalized_child_text,
    raw_record,
)


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
            acquisition_raw = first_value(
                fields,
                "dateAcquisition",
                "dateAchat",
                "anneeAcquisition",
                "dateSouscription",
                "dateDetention",
            )
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
