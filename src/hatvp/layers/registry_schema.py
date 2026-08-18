"""Typed physical schema for the anomaly registry artifact."""

from __future__ import annotations

import polars as pl


def registry_schema() -> dict[str, object]:
    """Return the Parquet/BigQuery field contract for anomaly_registry."""

    text_fields = (
        "anomaly_id anomaly_key rule_id severity declarant_key field period observed_value "
        "expected_value_or_range evidence record_ref first_seen last_seen superseded_by status "
        "declaration_id declaration_version source_snapshot_date source_format "
        "source_uri_or_object "
        "source_location candidate_value_or_range detected_at seen_snapshots snapshot_date"
    ).split()
    return {
        **{name: pl.String for name in text_fields},
        "is_latest_declaration": pl.Boolean,
        "previously_reported": pl.Boolean,
        "metric_eligible": pl.Boolean,
        "active_in_gold": pl.Boolean,
        "occurrence_count": pl.Int64,
    }


def registry_text_fields() -> tuple[str, ...]:
    """Return text fields for explicit-column loader and schema tests."""

    return tuple(name for name, dtype in registry_schema().items() if dtype == pl.String)


def registry_boolean_fields() -> tuple[str, ...]:
    """Return lifecycle fields that must remain typed booleans."""

    return tuple(name for name, dtype in registry_schema().items() if dtype == pl.Boolean)


def registry_numeric_fields() -> tuple[str, ...]:
    """Return count fields used by idempotency validation."""

    return tuple(name for name, dtype in registry_schema().items() if dtype == pl.Int64)


def registry_required_columns() -> tuple[str, ...]:
    """Return the deterministic physical column order used in Parquet."""

    return tuple(registry_schema())


def registry_statuses() -> tuple[str, ...]:
    """Return lifecycle states accepted by reporting and Gold selection."""

    return ("active", "known/reported", "superseded", "resolved", "regression")


def registry_partition_field() -> str:
    """Return the partition field shared by every analytical table."""

    return "snapshot_date"


def registry_has_lifecycle_contract() -> bool:
    """Confirm the schema includes all required lifecycle fields."""

    required = {"status", "first_seen", "last_seen", "active_in_gold", "previously_reported"}
    return required.issubset(registry_schema())


__all__ = [
    "registry_boolean_fields",
    "registry_has_lifecycle_contract",
    "registry_numeric_fields",
    "registry_partition_field",
    "registry_required_columns",
    "registry_schema",
    "registry_statuses",
    "registry_text_fields",
]
