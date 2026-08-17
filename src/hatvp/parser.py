"""Compatibility façade for the HATVP CSV and streaming XML parsers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import load_pipeline_config
from .parser_csv import parse_csv
from .parser_declarations import declaration_row as _declaration_row
from .parser_stream import empty_tables
from .parser_stream import parse_xml as _stream_parse_xml

_CONFIG = load_pipeline_config().parser
XML_ROOT_NAME = _CONFIG.xml_root
ALLOWED_TOP_LEVEL_CHILDREN = set(_CONFIG.allowed_top_level_children)
ASSET_SECTIONS = tuple(_CONFIG.sections["assets"])


def parse_xml(path: Path, snapshot_date: str) -> dict[str, list[dict[str, Any]]]:
    """Parse declarations with the legacy public signature."""

    return _stream_parse_xml(path, snapshot_date, declaration_parser=_declaration_row)


def parse_sources(
    csv_path: Path,
    xml_path: Path,
    snapshot_date: str,
) -> dict[str, list[dict[str, Any]]]:
    """Parse both source files and return the stable normalized table mapping."""

    tables = parse_xml(xml_path, snapshot_date)
    tables["liste"] = parse_csv(csv_path, snapshot_date)
    return tables


def parser_table_names() -> tuple[str, ...]:
    """Return the table order used by streaming parser output and tests."""

    return tuple(empty_tables())


__all__ = [
    "ALLOWED_TOP_LEVEL_CHILDREN",
    "ASSET_SECTIONS",
    "XML_ROOT_NAME",
    "parse_csv",
    "parse_sources",
    "parse_xml",
    "parser_table_names",
]
