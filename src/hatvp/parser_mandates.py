"""Mandate and annual remuneration row parsers."""

from __future__ import annotations

from typing import Any

from lxml import etree

from .models import ParseContext, ParserConfig
from .normalize import normalize_text, parse_french_number
from .xml_support import (
    child,
    date_fields,
    first_value,
    flatten_leaf_values,
    item_groups,
    normalized_child_text,
    raw_child_text,
    raw_record,
)


def mandate_item_fields(item: etree._Element) -> dict[str, Any]:
    values = flatten_leaf_values(item)
    start_raw, start = date_fields(values, "dateDebut")
    end_raw, end = date_fields(values, "dateFin")
    return {
        "description": normalize_text(
            first_value(values, "descriptionMandat", "description", "label")
        ),
        "commentaire": normalize_text(values.get("commentaire")),
        "employeur": normalize_text(values.get("employeur")),
        "date_debut_raw": start_raw,
        "date_debut": start,
        "date_fin_raw": end_raw,
        "date_fin": end,
    }


def remuneration_entries(item: etree._Element) -> list[dict[str, Any]]:
    remuneration = child(item, "remuneration")
    amount_container = child(remuneration, "montant")
    if remuneration is None or amount_container is None:
        return []
    basis_raw = raw_child_text(remuneration, "brutNet")
    annual = list(item for item in amount_container if item.tag.rsplit("}", 1)[-1] == "montant")
    candidates = annual or [remuneration]
    entries: list[dict[str, Any]] = []
    for candidate in candidates:
        year_raw = raw_child_text(candidate, "annee")
        value_raw = raw_child_text(candidate, "montant")
        if value_raw is None and candidate is remuneration:
            value_raw = raw_child_text(remuneration, "montant")
        if value_raw is None:
            continue
        entries.append(
            {
                "remuneration_basis_raw": basis_raw,
                "remuneration_basis": normalize_text(basis_raw),
                "remuneration_year_raw": year_raw,
                "remuneration_year": _parse_year(year_raw),
                "raw_value": value_raw,
                "normalized_value": parse_french_number(value_raw),
            }
        )
    return entries


def _parse_year(value: str | None) -> int | None:
    value = normalize_text(value)
    return int(value) if value and len(value) == 4 and value.isdigit() else None


def mandate_raw_record(item: etree._Element, entries: list[dict[str, Any]]) -> str:
    values = flatten_leaf_values(item)
    record = {key: value for key, value in values.items() if not key.startswith("remuneration_")}
    remuneration = child(item, "remuneration")
    record["remuneration"] = {
        "brutNet": raw_child_text(remuneration, "brutNet"),
        "amounts": [
            {"annee": row["remuneration_year_raw"], "montant": row["raw_value"]} for row in entries
        ],
        "raw_text": remuneration.text.strip()
        if remuneration is not None and remuneration.text
        else None,
    }
    return raw_record(record)


def mandate_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    uuid = normalized_child_text(element, "uuid")
    general = child(element, "general")
    mandate = child(general, "mandat")
    quality = child(general, "qualiteMandat")
    rows: list[dict[str, Any]] = []
    label = normalized_child_text(mandate, "label") or normalized_child_text(general, "mandat")
    if general is not None and (label or quality is not None):
        start_raw = raw_child_text(general, "dateDebutMandat")
        end_raw = raw_child_text(general, "dateFinMandat")
        rows.append(_general_mandate(uuid, context, label, quality, start_raw, end_raw))
    section = child(element, config.sections["mandate"])
    for index, item in enumerate(item_groups(section)):
        fields = mandate_item_fields(item)
        entries = remuneration_entries(item)
        scalar = entries[0] if len(entries) == 1 else None
        rows.append(_elected_mandate(uuid, context, index, fields, scalar, entries, item))
    return rows


def _general_mandate(
    uuid: str | None,
    context: ParseContext,
    label: str | None,
    quality: etree._Element | None,
    start_raw: str | None,
    end_raw: str | None,
) -> dict[str, Any]:
    return {
        "declaration_uuid": uuid,
        "snapshot_date": context.snapshot_date,
        "source_section": "general",
        "description": label,
        "mandate_type": normalized_child_text(quality, "typeMandat"),
        "commentaire": None,
        "employeur": None,
        "date_debut_raw": start_raw,
        "date_debut": date_fields({"value": start_raw}, "value")[1],
        "date_fin_raw": end_raw,
        "date_fin": date_fields({"value": end_raw}, "value")[1],
        "remuneration_raw": None,
        "remuneration_eur": None,
        "remuneration_year_raw": None,
        "remuneration_year": None,
        "remuneration_count": 0,
        "raw_record_json": None,
    }


def _elected_mandate(
    uuid: str | None,
    context: ParseContext,
    index: int,
    fields: dict[str, Any],
    scalar: dict[str, Any] | None,
    entries: list[dict[str, Any]],
    item: etree._Element,
) -> dict[str, Any]:
    return {
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
