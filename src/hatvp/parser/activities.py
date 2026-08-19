"""Activity and participation parsers for repeated declaration sections."""

from __future__ import annotations

from typing import Any

from lxml import etree

from ..models import ParseContext, ParserConfig
from ..normalize import normalize_text, parse_french_number
from ..xml_support import (
    child,
    date_fields,
    first_value,
    flatten_leaf_values,
    item_groups,
    normalized_child_text,
    raw_record,
)
from .mandate_fields import remuneration_entries


def activity_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    uuid = normalized_child_text(element, "uuid")
    rows: list[dict[str, Any]] = []
    for section_name in config.sections["activities"]:
        for index, item in enumerate(item_groups(child(element, section_name))):
            values = flatten_leaf_values(item)
            entries = remuneration_entries(item)
            start_raw, start = date_fields(values, "dateDebut")
            end_raw, end = date_fields(values, "dateFin")
            rows.append(
                {
                    "declaration_uuid": uuid,
                    "snapshot_date": context.snapshot_date,
                    "source_section": section_name,
                    "source_item_index": index,
                    "description": normalize_text(
                        first_value(values, *config.field_candidates["activity_description"])
                    ),
                    "employeur": normalize_text(
                        first_value(values, *config.field_candidates["activity_employer"])
                    ),
                    "date_debut_raw": start_raw,
                    "date_debut": start,
                    "date_fin_raw": end_raw,
                    "date_fin": end,
                    "remuneration_raw": entries[0]["raw_value"] if entries else None,
                    "raw_record_json": raw_record(values),
                }
            )
    return rows


def participation_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    uuid = normalized_child_text(element, "uuid")
    rows: list[dict[str, Any]] = []
    for section_name in config.sections["participations"]:
        for index, item in enumerate(item_groups(child(element, section_name))):
            values = flatten_leaf_values(item)
            valuation = first_value(values, "evaluation", "valeur", "valeurActuelle")
            rows.append(
                {
                    "declaration_uuid": uuid,
                    "snapshot_date": context.snapshot_date,
                    "source_section": section_name,
                    "source_item_index": index,
                    "company_name": normalize_text(
                        first_value(values, *config.field_candidates["participation_company"])
                    ),
                    "activity": normalize_text(values.get("activite")),
                    "commentaire": normalize_text(values.get("commentaire")),
                    "evaluation_raw": valuation,
                    "evaluation_eur": parse_french_number(valuation),
                    "capital_detenu_raw": values.get("capitalDetenu"),
                    "nombre_parts_raw": values.get("nombreParts"),
                    "remuneration_raw": values.get("remuneration"),
                    "raw_record_json": raw_record(values),
                }
            )
    return rows
