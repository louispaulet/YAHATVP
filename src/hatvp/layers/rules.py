"""Small HATVP-specific anomaly rules for compensation and source fields."""

from __future__ import annotations

from datetime import date
from typing import Any


def ratio_rule(value: float, previous: list[float]) -> bool:
    """Flag a tenfold jump/drop or a large change after stable history."""

    return any(
        (old and (value / old >= 10 or value / old <= 0.1))
        or (len(previous) >= 2 and old and abs(value - old) / old >= 4)
        for old in previous
    )


def factor_rule(value: float, previous: list[float]) -> list[float]:
    """Return decimal-factor candidates close to one historical value."""

    candidates = []
    for factor in (10.0, 100.0, 1000.0):
        for candidate in (value / factor, value * factor):
            if any(old and abs(candidate - old) / old <= 0.05 for old in previous):
                candidates.append(candidate)
    return sorted(set(candidates))


def digit_edit_rule(value: float, previous: list[float]) -> list[str]:
    """Find simple one-character edits that match a historical number."""

    observed = str(int(value))
    matches: list[str] = []
    for old in previous:
        candidate = str(int(old))
        if (
            len(observed) == len(candidate)
            and sum(a != b for a, b in zip(observed, candidate, strict=True)) == 1
        ):
            matches.append(candidate)
        if observed.replace("0", "", 1) == candidate or candidate.replace("0", "", 1) == observed:
            matches.append(candidate)
    return sorted(set(matches))


def concatenated_rule(value: float, previous: list[float], raw: str | None) -> list[str]:
    """Return plausible prefix/suffix segments for an unusually long value."""

    digits = "".join(character for character in (raw or str(int(value))) if character.isdigit())
    if len(digits) < 9:
        return []
    historical = {str(int(old)) for old in previous}
    splits = [digits[:index] + "+" + digits[index:] for index in range(3, len(digits) - 2)]
    return [
        split
        for split in splits
        if split.split("+")[0] in historical or split.split("+")[1] in historical
    ]


def implausible_birth(
    value: str | None, reference: str | None = None, max_age_years: int = 100
) -> bool:
    """Flag impossible dates and dates incompatible with an adult office holder."""

    if not value:
        return False
    try:
        born = date.fromisoformat(value)
        reference_date = date.fromisoformat(reference) if reference else date.today()
    except ValueError:
        return True
    age = (
        reference_date.year
        - born.year
        - ((reference_date.month, reference_date.day) < (born.month, born.day))
    )
    return born > reference_date or born.year < 1900 or age < 18 or age > max_age_years


def conflicting_sources(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Return cross-format values when a row carries contradictory evidence."""

    values = row.get("cross_format_values") or row.get("source_values")
    if not isinstance(values, dict):
        return []
    distinct = {str(value) for value in values.values() if value not in (None, "")}
    return (
        [{"format": key, "value": value} for key, value in values.items()]
        if len(distinct) > 1
        else []
    )
