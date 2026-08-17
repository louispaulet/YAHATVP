"""Streaming XML driver that delegates rows to section-specific components."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from lxml import etree

from .config import load_pipeline_config
from .models import ParseContext, Row, TableSet
from .parser_activities import activity_rows, participation_rows
from .parser_declarations import declaration_row, person_row
from .parser_finance import asset_rows, liability_rows
from .parser_income import income_rows, mandate_income_rows
from .parser_mandates import mandate_rows, remuneration_rows
from .xml_support import local_name


def empty_tables() -> TableSet:
    return {
        name: []
        for name in (
            "liste",
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
    }


def parse_xml(
    path: Path, snapshot_date: str, declaration_parser: Callable[..., Row] = declaration_row
) -> TableSet:
    config = load_pipeline_config().parser
    context = ParseContext(snapshot_date)
    tables = empty_tables()
    context_reader = etree.iterparse(
        str(path),
        events=("start", "end"),
        recover=False,
        huge_tree=True,
        load_dtd=False,
        no_network=True,
        resolve_entities=False,
    )
    root: etree._Element | None = None
    top_level_count = 0
    declaration_count = 0
    try:
        for event, element in context_reader:
            if event == "start":
                root, top_level_count = _validate_start(root, element, top_level_count, config)
                continue
            if local_name(element.tag) != "declaration":
                continue
            declaration_count += 1
            _append_declaration(tables, element, context, config, declaration_parser)
            _clear(element)
    except etree.XMLSyntaxError as exc:
        raise ValueError(f"HATVP XML is malformed: {exc}") from exc
    if root is None:
        raise ValueError("HATVP XML is empty")
    if top_level_count == 0:
        raise ValueError("HATVP XML has no top-level declaration container")
    if declaration_count == 0:
        raise ValueError("HATVP XML contains no declaration records")
    return tables


def _validate_start(
    root: etree._Element | None, element: etree._Element, count: int, config
) -> tuple[etree._Element, int]:
    if root is None:
        if local_name(element.tag) != config.xml_root:
            raise ValueError(f"HATVP XML has unexpected root element: {local_name(element.tag)}")
        return element, count
    if element.getparent() is root:
        child_name = local_name(element.tag)
        if child_name not in config.allowed_top_level_children:
            raise ValueError(f"HATVP XML has invalid top-level element: {child_name}")
        count += 1
    return root, count


def _append_declaration(
    tables: TableSet, element: etree._Element, context: ParseContext, config, declaration_parser
) -> None:
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


def _clear(element: etree._Element) -> None:
    parent = element.getparent()
    element.clear()
    if parent is not None:
        while element.getprevious() is not None:
            del parent[0]
