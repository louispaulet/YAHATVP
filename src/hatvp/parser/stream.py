"""Streaming XML driver that delegates rows to section-specific components."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from lxml import etree

from ..config import load_pipeline_config
from ..models import Row, TableSet
from ..xml_support import local_name
from .declarations import declaration_row
from .dispatch import append_declaration
from .provenance import context_for

TABLE_NAMES = (
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


def empty_tables() -> TableSet:
    return {name: [] for name in TABLE_NAMES}


def parse_xml(
    path: Path,
    snapshot_date: str,
    declaration_parser: Callable[..., Row] = declaration_row,
    source_metadata: Mapping[str, Any] | None = None,
) -> TableSet:
    config = load_pipeline_config().parser
    context = context_for(snapshot_date, "declarations.xml", "xml", str(path), source_metadata)
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
            append_declaration(
                tables, element, context, config, declaration_parser, declaration_count - 1
            )
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


def _clear(element: etree._Element) -> None:
    parent = element.getparent()
    element.clear()
    if parent is not None:
        while element.getprevious() is not None:
            del parent[0]
