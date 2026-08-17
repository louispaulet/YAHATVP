"""Shared scalar and remuneration extraction for mandate components."""

from __future__ import annotations

from typing import Any

from lxml import etree

from .normalize import normalize_text, parse_french_number
from .xml_support import (
    child,
    date_fields,
    first_value,
    flatten_leaf_values,
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
    annual = [node for node in amount_container if node.tag.rsplit("}", 1)[-1] == "montant"]
    entries: list[dict[str, Any]] = []
    for candidate in annual or [remuneration]:
        year_raw = raw_child_text(candidate, "annee")
        value_raw = raw_child_text(candidate, "montant") or (
            raw_child_text(remuneration, "montant") if candidate is remuneration else None
        )
        if value_raw is not None:
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


def _parse_year(value: str | None) -> int | None:
    normalized = normalize_text(value)
    return int(normalized) if normalized and len(normalized) == 4 and normalized.isdigit() else None


__all__ = ["mandate_item_fields", "mandate_raw_record", "remuneration_entries"]
