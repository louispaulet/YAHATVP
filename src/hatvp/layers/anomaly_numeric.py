"""Numeric historical anomaly rules for income values."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .anomaly_support import declarant_key, numeric_value, occurrence, role_name
from .rules import concatenated_rule, digit_edit_rule, factor_rule, ratio_rule


def numeric_anomalies(
    rows: list[dict[str, Any]], parents: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Compare each value with all historical values for the same source role."""

    history = _history_by_identity(rows, parents)
    occurrences: list[dict[str, Any]] = []
    for row in rows:
        parent = parents.get(row.get("bronze_record_key", ""), {})
        value = numeric_value(row)
        if value is None:
            continue
        prior = _prior_values(row, parent, history, value)
        if ratio_rule(value, prior):
            occurrences.append(
                occurrence(
                    "COMP_YOY_CHANGE", row, parent, "normalized_value", {"prior_values": prior}
                )
            )
        if value > 500_000:
            occurrences.append(
                occurrence(
                    "COMP_IMPLAUSIBLE_AMOUNT",
                    row,
                    parent,
                    "normalized_value",
                    {"threshold": 500_000},
                )
            )
        candidates = (
            ("COMP_FACTOR_ERROR", factor_rule(value, prior)),
            ("COMP_DIGIT_EDIT", digit_edit_rule(value, prior)),
            ("COMP_CONCATENATED_VALUE", concatenated_rule(value, prior, row.get("raw_value"))),
        )
        for rule, found in candidates:
            if found:
                occurrences.append(
                    occurrence(rule, row, parent, "normalized_value", {"candidates": found})
                )
    return occurrences


def _history_by_identity(
    rows: list[dict[str, Any]], parents: dict[str, dict[str, Any]]
) -> defaultdict[tuple[str, str], list[float]]:
    history: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        parent = parents.get(row.get("bronze_record_key", ""), {})
        value = numeric_value(row)
        if value is not None:
            history[(declarant_key(row, parent), role_name(row))].append(value)
    return history


def _prior_values(
    row: dict[str, Any],
    parent: dict[str, Any],
    history: defaultdict[tuple[str, str], list[float]],
    value: float,
) -> list[float]:
    return [old for old in history[(declarant_key(row, parent), role_name(row))] if old != value]


def numeric_rule_ids() -> tuple[str, ...]:
    """Expose the stable numeric rule inventory for documentation/tests."""

    return (
        "COMP_YOY_CHANGE",
        "COMP_IMPLAUSIBLE_AMOUNT",
        "COMP_FACTOR_ERROR",
        "COMP_DIGIT_EDIT",
        "COMP_CONCATENATED_VALUE",
    )


__all__ = ["numeric_anomalies", "numeric_rule_ids"]
