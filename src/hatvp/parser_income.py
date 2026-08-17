"""Income and unified annual remuneration parsers."""

from __future__ import annotations

from typing import Any

from lxml import etree

from .models import ParseContext, ParserConfig
from .normalize import normalize_text, parse_french_number
from .parser_mandates import mandate_item_fields, mandate_raw_record, remuneration_entries
from .xml_support import child, flatten_leaf_values, item_groups, normalized_child_text, raw_record


def income_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    uuid = normalized_child_text(element, "uuid")
    section = child(element, config.sections["income"])
    rows: list[dict[str, Any]] = []
    for item_index, item in enumerate(item_groups(section)):
        values = flatten_leaf_values(item)
        year = normalize_text(values.get("annee"))
        categories = [
            node for node in item if node.tag.rsplit("}", 1)[-1].startswith("revenuMandatItem")
        ]
        populated = 0
        for category_index, category in enumerate(categories):
            category_values = flatten_leaf_values(category)
            raw_value = category_values.get("revenuElu")
            spouse_raw = category_values.get("revenuConjoint")
            if raw_value is None and spouse_raw is None:
                continue
            populated += 1
            rows.append(
                _income_row(
                    uuid,
                    context,
                    item_index,
                    category_index,
                    year,
                    category_values,
                    raw_value,
                    spouse_raw,
                    raw_record(category_values),
                )
            )
        if populated == 0 and (
            values.get("totalElu") is not None or values.get("totalConjoint") is not None
        ):
            rows.append(
                _income_row(
                    uuid,
                    context,
                    item_index,
                    None,
                    year,
                    values,
                    values.get("totalElu"),
                    values.get("totalConjoint"),
                    raw_record(values),
                    income_type="totalElu",
                )
            )
    return rows


def _income_row(
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


def mandate_income_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    uuid = normalized_child_text(element, "uuid")
    section = child(element, config.sections["mandate"])
    rows: list[dict[str, Any]] = []
    for item_index, item in enumerate(item_groups(section)):
        fields = mandate_item_fields(item)
        entries = remuneration_entries(item)
        source_record = mandate_raw_record(item, entries)
        for remuneration_index, entry in enumerate(entries):
            rows.append(
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
                    "raw_record_json": source_record,
                    "remuneration_index": remuneration_index,
                }
            )
    return rows
