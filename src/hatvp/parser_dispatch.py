"""Dispatch one declaration through every normalized table component."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from lxml import etree

from .models import ParseContext, Row, TableSet
from .parser_activities import activity_rows, participation_rows
from .parser_declarations import person_row
from .parser_finance import asset_rows, liability_rows
from .parser_income import income_rows, mandate_income_rows
from .parser_mandates import mandate_rows, remuneration_rows


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


__all__ = ["append_declaration"]
