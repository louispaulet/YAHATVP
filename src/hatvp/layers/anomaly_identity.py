"""Identity anomaly rules for HATVP declaration history."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..config import Settings
from .anomaly_support import declarant_key, occurrence
from .rules import implausible_birth


def identity_anomalies(
    rows: list[dict[str, Any]],
    parents: dict[str, dict[str, Any]],
    max_age_years: int | None = None,
) -> list[dict[str, Any]]:
    """Flag missing identity keys, impossible dates, and conflicting birth dates."""

    threshold = (
        max_age_years if max_age_years is not None else Settings().hatvp_person_dob_max_age_years
    )
    results: list[dict[str, Any]] = []
    seen: defaultdict[str, set[str]] = defaultdict(set)
    for row in rows:
        parent = parents.get(row.get("bronze_record_key", ""), {})
        identity = declarant_key(row, parent)
        if not row.get("declaration_uuid"):
            results.append(
                occurrence(
                    "PERSON_IDENTITY_REVIEW",
                    row,
                    parent,
                    "declaration_uuid",
                    {"reason": "no stable source identifier"},
                )
            )
        if implausible_birth(row.get("date_naissance"), parent.get("date_depot"), threshold):
            results.append(
                occurrence(
                    "PERSON_DOB_IMPLAUSIBLE",
                    row,
                    parent,
                    "date_naissance",
                    {"raw": row.get("date_naissance_raw")},
                )
            )
        if row.get("date_naissance"):
            seen[identity].add(str(row["date_naissance"]))
    for row in rows:
        parent = parents.get(row.get("bronze_record_key", ""), {})
        identity = declarant_key(row, parent)
        if len(seen[identity]) > 1:
            results.append(
                occurrence(
                    "PERSON_DOB_CONFLICT",
                    row,
                    parent,
                    "date_naissance",
                    {"values": sorted(seen[identity])},
                )
            )
    return results


def identity_rule_ids() -> tuple[str, ...]:
    """Expose identity rules for acceptance coverage."""

    return ("PERSON_IDENTITY_REVIEW", "PERSON_DOB_IMPLAUSIBLE", "PERSON_DOB_CONFLICT")


def identity_is_stable(row: dict[str, Any]) -> bool:
    """Return whether a row has a stable source identity instead of review fallback."""

    return bool(row.get("declaration_uuid") or row.get("source_record_id"))


def birth_date_values(rows: list[dict[str, Any]]) -> tuple[str, ...]:
    """Return distinct parsed birth dates for diagnostics."""

    return tuple(sorted({str(row["date_naissance"]) for row in rows if row.get("date_naissance")}))


__all__ = ["birth_date_values", "identity_anomalies", "identity_is_stable", "identity_rule_ids"]
