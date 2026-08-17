"""Parser for the optional general mandate section of a declaration."""

from __future__ import annotations

from typing import Any

from lxml import etree

from .models import ParseContext
from .xml_support import date_fields, normalized_child_text, raw_child_text


def general_mandate_row(
    uuid: str | None,
    context: ParseContext,
    label: str | None,
    quality: etree._Element | None,
    general: etree._Element,
) -> dict[str, Any]:
    """Normalize the general mandate dates and identity fields."""

    start_raw = raw_child_text(general, "dateDebutMandat")
    end_raw = raw_child_text(general, "dateFinMandat")
    start = date_fields({"value": start_raw}, "value")[1]
    end = date_fields({"value": end_raw}, "value")[1]
    return {
        "declaration_uuid": uuid,
        "snapshot_date": context.snapshot_date,
        "source_section": "general",
        "description": label,
        "mandate_type": normalized_child_text(quality, "typeMandat"),
        "commentaire": None,
        "employeur": None,
        "date_debut_raw": start_raw,
        "date_debut": start,
        "date_fin_raw": end_raw,
        "date_fin": end,
        "remuneration_raw": None,
        "remuneration_eur": None,
        "remuneration_year_raw": None,
        "remuneration_year": None,
        "remuneration_count": 0,
        "raw_record_json": None,
    }


def has_general_values(general: etree._Element | None, label: str | None) -> bool:
    """Return whether the optional general section can produce a row."""

    if general is None:
        return False
    quality = general.find("qualiteMandat")
    return bool(label or quality is not None)


def general_dates(general: etree._Element) -> tuple[str | None, str | None]:
    """Return normalized start and end dates for direct general-section tests."""

    start_raw = raw_child_text(general, "dateDebutMandat")
    end_raw = raw_child_text(general, "dateFinMandat")
    return (
        date_fields({"value": start_raw}, "value")[1],
        date_fields({"value": end_raw}, "value")[1],
    )


def general_is_dated(general: etree._Element) -> bool:
    """Return whether at least one general mandate boundary date is present."""

    return any(general_dates(general))


__all__ = ["general_dates", "general_mandate_row", "has_general_values"]
