"""Source-preserving quality labels for declarant birth dates."""

from __future__ import annotations

from typing import Any

REVIEW_RULES = frozenset({"PERSON_DOB_IMPLAUSIBLE", "PERSON_DOB_CONFLICT"})
QUALITY_STATUSES = (
    "valid",
    "missing",
    "invalid",
    "implausible",
    "conflicting",
    "implausible_conflicting",
)


def rule_ids(items: list[dict[str, Any]]) -> set[str]:
    """Return only DOB rule IDs attached to one annotated person row."""

    return {str(item.get("rule_id")) for item in items} & REVIEW_RULES


def parsed_state(row: dict[str, Any]) -> str:
    """Classify missing and unparseable values before anomaly rules are applied."""

    raw = row.get("date_naissance_raw")
    parsed = row.get("date_naissance")
    if raw and not parsed:
        return "invalid"
    if not parsed:
        return "missing"
    return "valid"


def status_for(row: dict[str, Any], items: list[dict[str, Any]]) -> str:
    """Return the combined quality status for a parsed DOB and its rules."""

    state = parsed_state(row)
    if state != "valid":
        return state
    rules = rule_ids(items)
    if rules == REVIEW_RULES:
        return "implausible_conflicting"
    if "PERSON_DOB_IMPLAUSIBLE" in rules:
        return "implausible"
    if "PERSON_DOB_CONFLICT" in rules:
        return "conflicting"
    return state


def reason_for(items: list[dict[str, Any]]) -> str | None:
    """Return stable, human-readable DOB rule IDs for quality review."""

    return ", ".join(sorted(rule_ids(items))) or None


def quality_fields(row: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, str | None]:
    """Return explicit DOB quality metadata without replacing the observed date."""

    status = status_for(row, items)
    reason = reason_for(items)
    if status == "invalid" and reason is None:
        reason = "unparseable source value"
    return {
        "date_naissance_quality_status": status,
        "date_naissance_quality_reason": reason,
    }


def is_review_status(status: str | None) -> bool:
    """Return whether a quality status should be shown as a review signal."""

    return status in {"invalid", "implausible", "conflicting", "implausible_conflicting"}


__all__ = ["QUALITY_STATUSES", "is_review_status", "quality_fields", "reason_for", "status_for"]
