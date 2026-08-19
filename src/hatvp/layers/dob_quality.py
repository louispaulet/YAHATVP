"""Source-preserving quality labels for declarant birth dates."""

from __future__ import annotations

from typing import Any


def quality_fields(row: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, str | None]:
    """Return explicit DOB quality metadata without replacing the observed date."""

    raw = row.get("date_naissance_raw")
    parsed = row.get("date_naissance")
    rules = {str(item.get("rule_id")) for item in items}
    if raw and not parsed:
        return {
            "date_naissance_quality_status": "invalid",
            "date_naissance_quality_reason": "unparseable source value",
        }
    if not parsed:
        return {"date_naissance_quality_status": "missing", "date_naissance_quality_reason": None}
    if "PERSON_DOB_IMPLAUSIBLE" in rules and "PERSON_DOB_CONFLICT" in rules:
        status = "implausible_conflicting"
    elif "PERSON_DOB_IMPLAUSIBLE" in rules:
        status = "implausible"
    elif "PERSON_DOB_CONFLICT" in rules:
        status = "conflicting"
    else:
        status = "valid"
    reason = ", ".join(sorted(rules & {"PERSON_DOB_IMPLAUSIBLE", "PERSON_DOB_CONFLICT"})) or None
    return {"date_naissance_quality_status": status, "date_naissance_quality_reason": reason}


__all__ = ["quality_fields"]
