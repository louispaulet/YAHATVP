"""Shared constants and safe SQL fragments for the dashboard bridge."""

from __future__ import annotations

import re
from collections.abc import Iterable

TABLES = ("declarations", "people", "incomes", "assets")
VIEWS = ("overview", "income", "assets", "declarations", "gender")
SEARCH_LIMIT = 50
IDENTIFIER = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_identifier(value: str) -> str:
    """Allow only project and dataset identifiers supplied by deployment config."""

    if not IDENTIFIER.fullmatch(value):
        raise ValueError("Invalid BigQuery project or dataset identifier")
    return value


def dataset_prefix(project: str, dataset: str) -> str:
    """Return a quoted project and dataset prefix after identifier validation."""

    return f"`{validate_identifier(project)}.{validate_identifier(dataset)}`"


def table(prefix: str, name: str) -> str:
    """Append one fixed table name to a validated dataset prefix."""

    if name not in TABLES:
        raise ValueError("Invalid dashboard table")
    return f"{prefix}.gold_{name}"


def latest_cte(prefix: str) -> str:
    """Build the shared latest-snapshot CTE used by every bridge query."""

    declarations = table(prefix, "declarations")
    return f"WITH latest AS (SELECT MAX(snapshot_date) AS snapshot_date FROM {declarations})"


def normalized_contains(field: str, term: str = "s.term") -> str:
    """Build a literal, accent-insensitive substring predicate."""

    return f"STRPOS(NORMALIZE_AND_CASEFOLD(COALESCE({field}, '')), {term}) > 0"


def any_predicates(predicates: Iterable[str]) -> str:
    """Join fixed predicates into a readable SQL OR expression."""

    return "\n      OR ".join(predicates)


def exists_text_match(table_name: str, alias: str, predicates: Iterable[str]) -> str:
    """Build an existence check for fields in one child Gold table."""

    conditions = any_predicates(predicates)
    return f"""OR EXISTS (
        SELECT 1 FROM {{prefix}}.gold_{table_name} {alias}
        WHERE {alias}.declaration_uuid = d.declaration_uuid
          AND {alias}.snapshot_date = d.snapshot_date
          AND (
            {conditions}
          )
      )"""


__all__ = [
    "SEARCH_LIMIT",
    "TABLES",
    "VIEWS",
    "any_predicates",
    "dataset_prefix",
    "exists_text_match",
    "latest_cte",
    "normalized_contains",
    "table",
    "validate_identifier",
]
