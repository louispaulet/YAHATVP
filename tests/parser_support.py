"""Fixture and row-selection helpers shared by parser behavior tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hatvp.parser import parse_csv, parse_xml

FIXTURES = Path(__file__).parent / "fixtures"
SNAPSHOT = "2026-08-16"


def xml_tables(name: str = "declarations.xml") -> dict[str, list[dict[str, Any]]]:
    """Parse one XML fixture through the stable public parser boundary."""

    return parse_xml(FIXTURES / name, SNAPSHOT)


def csv_rows(name: str = "liste.csv") -> list[dict[str, Any]]:
    """Parse one listing fixture through the stable public CSV boundary."""

    return parse_csv(FIXTURES / name, SNAPSHOT)


def rows_for(
    tables: dict[str, list[dict[str, Any]]], table_name: str, declaration_uuid: str
) -> list[dict[str, Any]]:
    """Select rows belonging to one declaration without changing their order."""

    return [row for row in tables[table_name] if row.get("declaration_uuid") == declaration_uuid]


def first_row(
    tables: dict[str, list[dict[str, Any]]], table_name: str, **match: Any
) -> dict[str, Any]:
    """Return the first row matching a small fixture predicate."""

    return next(row for row in tables[table_name] if all(row.get(k) == v for k, v in match.items()))


def raw_record(row: dict[str, Any]) -> dict[str, Any]:
    """Decode the JSON source record retained on a normalized row."""

    value = row.get("raw_record_json")
    return json.loads(value) if isinstance(value, str) else {}


def declaration_ids(tables: dict[str, list[dict[str, Any]]]) -> set[str]:
    """Return declaration identifiers as a compact structural assertion."""

    return {row["declaration_uuid"] for row in tables["declarations"]}


def table_lengths(tables: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    """Return deterministic table row counts for parser acceptance checks."""

    return {name: len(rows) for name, rows in tables.items()}


def asset_sections(tables: dict[str, list[dict[str, Any]]]) -> set[str]:
    """Return the source DTO names represented by normalized asset rows."""

    return {row["source_section"] for row in tables["assets"]}


def has_provenance(row: dict[str, Any]) -> bool:
    """Return whether a normalized row carries the required snapshot provenance."""

    return bool(row.get("snapshot_date") and row.get("source_file"))


def nonempty_tables(tables: dict[str, list[dict[str, Any]]]) -> tuple[str, ...]:
    """Return populated table names in deterministic parser output order."""

    return tuple(name for name, rows in tables.items() if rows)
