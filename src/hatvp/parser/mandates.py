"""Mandate and annual remuneration row parsers."""

from __future__ import annotations

from typing import Any

from lxml import etree

from ..models import ParseContext, ParserConfig
from ..xml_support import child, item_groups, normalized_child_text
from .mandate_fields import mandate_item_fields, mandate_raw_record, remuneration_entries
from .mandate_general import general_mandate_row, has_general_values


def mandate_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    uuid = normalized_child_text(element, "uuid")
    general = child(element, "general")
    quality = child(general, "qualiteMandat")
    label = normalized_child_text(child(general, "mandat"), "label") or normalized_child_text(
        general, "mandat"
    )
    rows = (
        [general_mandate_row(uuid, context, label, quality, general)]
        if has_general_values(general, label)
        else []
    )
    section = child(element, config.sections["mandate"])
    for index, item in enumerate(item_groups(section)):
        fields = mandate_item_fields(item)
        entries = remuneration_entries(item)
        scalar = entries[0] if len(entries) == 1 else None
        rows.append(
            {
                "declaration_uuid": uuid,
                "snapshot_date": context.snapshot_date,
                "source_section": "mandatElectifDto",
                "source_item_index": index,
                **fields,
                "mandate_type": None,
                "remuneration_raw": scalar["raw_value"] if scalar else None,
                "remuneration_eur": scalar["normalized_value"] if scalar else None,
                "remuneration_year_raw": scalar["remuneration_year_raw"] if scalar else None,
                "remuneration_year": scalar["remuneration_year"] if scalar else None,
                "remuneration_count": len(entries),
                "raw_record_json": mandate_raw_record(item, entries),
            }
        )
    return rows


def remuneration_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    uuid = normalized_child_text(element, "uuid")
    section = child(element, config.sections["mandate"])
    rows: list[dict[str, Any]] = []
    for item_index, item in enumerate(item_groups(section)):
        fields = mandate_item_fields(item)
        entries = remuneration_entries(item)
        record = mandate_raw_record(item, entries)
        for remuneration_index, entry in enumerate(entries):
            rows.append(
                {
                    "declaration_uuid": uuid,
                    "snapshot_date": context.snapshot_date,
                    "source_section": "mandatElectifDto",
                    "source_item_index": item_index,
                    "remuneration_index": remuneration_index,
                    "description": fields["description"],
                    "commentaire": fields["commentaire"],
                    "employeur": fields["employeur"],
                    "date_debut_raw": fields["date_debut_raw"],
                    "date_debut": fields["date_debut"],
                    "date_fin_raw": fields["date_fin_raw"],
                    "date_fin": fields["date_fin"],
                    **entry,
                    "quality_status": "OK",
                    "quality_reason": None,
                    "raw_record_json": record,
                }
            )
    return rows


__all__ = [
    "mandate_item_fields",
    "mandate_raw_record",
    "mandate_rows",
    "remuneration_entries",
    "remuneration_rows",
]
