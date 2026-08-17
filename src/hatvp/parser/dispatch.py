"""Dispatch one declaration through every normalized table component."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from lxml import etree

from ..models import ParseContext, Row, TableSet
from .activities import activity_rows, participation_rows
from .declarations import person_row
from .finance import asset_rows, liability_rows
from .income import income_rows, mandate_income_rows
from .mandates import mandate_rows, remuneration_rows

COMPONENT_TABLES = (
    "declarations",
    "people",
    "mandates",
    "mandate_remunerations",
    "activities",
    "participations",
    "incomes",
    "assets",
    "liabilities",
)


def append_declaration(
    tables: TableSet,
    element: etree._Element,
    context: ParseContext,
    config: Any,
    declaration_parser: Callable[..., Row],
) -> None:
    """Append all rows while preserving the legacy table order."""

    tables["declarations"].append(declaration_parser(element, context, config))
    tables["people"].append(person_row(element, context))
    tables["mandates"].extend(mandate_rows(element, context, config))
    tables["mandate_remunerations"].extend(remuneration_rows(element, context, config))
    tables["activities"].extend(activity_rows(element, context, config))
    tables["participations"].extend(participation_rows(element, context, config))
    tables["incomes"].extend(income_rows(element, context, config))
    tables["incomes"].extend(mandate_income_rows(element, context, config))
    tables["assets"].extend(asset_rows(element, context, config))
    tables["liabilities"].extend(liability_rows(element, context, config))


def component_table_names() -> tuple[str, ...]:
    """Return the normalized tables populated by one XML declaration."""

    return COMPONENT_TABLES


def append_rows(tables: TableSet, table_name: str, rows: list[Row]) -> None:
    """Append rows through one shared boundary used by component tests."""

    if table_name not in tables:
        raise KeyError(f"Unknown parser output table: {table_name}")
    tables[table_name].extend(rows)


def output_table_count(tables: TableSet) -> int:
    """Count normalized output tables available after one declaration dispatch."""

    return sum(name in tables for name in COMPONENT_TABLES)


__all__ = ["COMPONENT_TABLES", "append_declaration", "append_rows", "component_table_names"]
