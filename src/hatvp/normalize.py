from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

MISSING_MARKERS = {
    "",
    "neant",
    "néant",
    "n/a",
    "na",
    "null",
    "none",
    "[données non publiées]",
}


def raw_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned or None


def normalize_text(value: str | None) -> str | None:
    cleaned = raw_text(value)
    if cleaned is None or cleaned.casefold() in MISSING_MARKERS:
        return None
    return cleaned


def parse_french_number(value: str | int | float | None) -> float | None:
    """Parse common French monetary formats without changing the source value."""

    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = normalize_text(value)
    if cleaned is None:
        return None

    negative = cleaned.startswith("(") and cleaned.endswith(")")
    if negative:
        cleaned = cleaned[1:-1]
    cleaned = (
        cleaned.replace("€", "")
        .replace("EUR", "")
        .replace("eur", "")
        .replace("%", "")
        .replace("\u202f", "")
        .replace("\u00a0", "")
        .replace(" ", "")
    )
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif cleaned.count(".") > 1:
        cleaned = cleaned.replace(".", "")
    try:
        number = Decimal(cleaned)
    except InvalidOperation:
        return None
    if negative:
        number = -number
    return float(number)


def parse_date(value: str | None) -> str | None:
    raw = raw_text(value)
    if raw is None:
        return None
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%m/%Y", "%Y-%m-%d", "%Y-%m"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def parse_year(value: str | None) -> int | None:
    """Extract a four-digit year from a date, month, or year source value."""

    raw = raw_text(value)
    if raw is None:
        return None
    parsed = parse_date(raw)
    if parsed:
        return int(parsed[:4])
    return int(raw) if re.fullmatch(r"\d{4}", raw) else None
