"""Historical anomaly detection orchestration for source-shaped Bronze rows."""

from __future__ import annotations

from typing import Any

from .anomaly_conflict import conflict_anomalies
from .anomaly_identity import identity_anomalies
from .anomaly_numeric import numeric_anomalies
from .anomaly_source import source_anomalies
from .anomaly_support import parent_map, record_ref

NUMERIC_TABLES = ("incomes",)
IGNORED_INCOME_RULE_IDS = frozenset({"COMP_DIGIT_EDIT", "COMP_YOY_CHANGE"})


def detect_anomalies(
    tables: dict[str, list[dict[str, Any]]],
    history: dict[str, list[dict[str, Any]]],
    registry: list[dict[str, Any]] | None = None,
    dob_max_age_years: int | None = None,
) -> list[dict[str, Any]]:
    """Run all source-preserving rules over current rows plus historical context."""

    combined = {name: [*history.get(name, []), *tables.get(name, [])] for name in tables}
    parents = parent_map(combined)
    numeric_rows = _tag_rows(combined, NUMERIC_TABLES)
    income_rows = _tag_rows(combined, ("incomes",))
    people_rows = _tag_rows(combined, ("people",))
    current_numeric = _tag_rows(tables, NUMERIC_TABLES)
    items = [
        item
        for item in numeric_anomalies(numeric_rows, parents)
        if item["rule_id"] not in IGNORED_INCOME_RULE_IDS
    ]
    items.extend(conflict_anomalies(income_rows, parents))
    items.extend(identity_anomalies(people_rows, parents, dob_max_age_years))
    items.extend(source_anomalies(current_numeric, parents))
    return _deduplicate(items, registry or [])


def _tag_rows(
    tables: dict[str, list[dict[str, Any]]], names: tuple[str, ...]
) -> list[dict[str, Any]]:
    return [dict(row, _table=name) for name in names for row in tables.get(name, [])]


def _deduplicate(
    items: list[dict[str, Any]], registry: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    known = {item.get("anomaly_key") for item in registry}
    states = {item.get("anomaly_key"): item.get("status") for item in registry}
    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in items:
        item["anomaly_key"] = _anomaly_key(item)
        item["previously_reported"] = item["anomaly_key"] in known
        unique[(item["record_ref"], item["rule_id"], "")] = item
        if item["previously_reported"]:
            rule = (
                "ANOMALY_REGRESSION"
                if states.get(item["anomaly_key"]) in {"superseded", "resolved"}
                else "ANOMALY_KNOWN"
            )
            unique[(item["record_ref"], rule, item["rule_id"])] = dict(
                item, rule_id=rule, original_rule_id=item["rule_id"]
            )
    return list(unique.values())


def _anomaly_key(item: dict[str, Any]) -> str:
    """Use the documented identity/field/period/value registry key."""

    fields = ("declarant_key", "field", "period", "observed_value")
    return "|".join(str(item.get(field) or "") for field in fields)


def anomaly_rule_ids() -> tuple[str, ...]:
    """Expose the stable rule inventory for README and acceptance checks."""

    return (
        "COMP_YOY_CHANGE",
        "COMP_IMPLAUSIBLE_AMOUNT",
        "COMP_FACTOR_ERROR",
        "COMP_CONCATENATED_VALUE",
        "COMP_DIGIT_EDIT",
        "COMP_CONFLICT_SAME_PERIOD",
        "COMP_SUPERSEDED_DECLARATION",
        "GEO_DEPARTMENT_MUNICIPALITY",
        "PERSON_DOB_IMPLAUSIBLE",
        "SOURCE_CROSS_FORMAT",
        "ANOMALY_KNOWN",
        "ANOMALY_REGRESSION",
    )


__all__ = ["NUMERIC_TABLES", "anomaly_rule_ids", "detect_anomalies", "parent_map", "record_ref"]
