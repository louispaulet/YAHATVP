"""Dispatch one declaration through every normalized table component."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Any

from lxml import etree

from ..models import ParseContext, Row, TableSet
from ..xml_support import child, normalized_child_text
from .activities import activity_rows, participation_rows
from .activity_income import activity_income_rows
from .declarations import person_row
from .finance import asset_rows, liability_rows
from .income import income_rows, mandate_income_rows
from .mandates import mandate_rows, remuneration_rows
from .provenance import apply_provenance, record_key, source_location

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
    declaration_index: int = 0,
) -> None:
    """Append all rows while preserving the legacy table order."""

    general = child(element, "general")
    local_context = replace(
        context,
        declaration_version=normalized_child_text(element, "declarationVersion"),
        declaration_modificative=normalized_child_text(general, "declarationModificative"),
    )
    starts = {name: len(tables[name]) for name in COMPONENT_TABLES}
    tables["declarations"].append(declaration_parser(element, local_context, config))
    tables["people"].append(person_row(element, local_context))
    tables["mandates"].extend(mandate_rows(element, local_context, config))
    tables["mandate_remunerations"].extend(remuneration_rows(element, local_context, config))
    tables["activities"].extend(activity_rows(element, local_context, config))
    tables["participations"].extend(participation_rows(element, local_context, config))
    tables["incomes"].extend(income_rows(element, local_context, config))
    tables["incomes"].extend(activity_income_rows(element, local_context, config))
    tables["incomes"].extend(mandate_income_rows(element, local_context, config))
    tables["assets"].extend(asset_rows(element, local_context, config))
    tables["liabilities"].extend(liability_rows(element, local_context, config))
    source_id = normalized_child_text(element, "uuid")
    key = record_key(local_context, source_id, declaration_index)
    base = f"{context.source_file}#/declaration[{declaration_index}]"
    for name in COMPONENT_TABLES:
        for row in tables[name][starts[name] :]:
            apply_provenance(row, local_context, key, source_id, source_location(row, base))


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
