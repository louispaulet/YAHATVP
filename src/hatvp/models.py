"""Small typed boundaries shared by the HATVP pipeline components."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

type Row = dict[str, Any]
type TableRows = list[Row]
type TableSet = dict[str, TableRows]
type PipelineStatus = Literal["NO_CHANGE", "SUCCESS", "SUCCESS_WITH_WARNINGS", "FAILED"]


@dataclass(frozen=True)
class ParserConfig:
    """Schema-sensitive parser settings loaded from the packaged YAML file."""

    xml_root: str
    allowed_top_level_children: tuple[str, ...]
    sections: dict[str, Any]
    field_candidates: dict[str, tuple[str, ...]]
    csv_delimiter: str
    csv_identity_columns: tuple[str, ...]


@dataclass(frozen=True)
class PipelineConfig:
    """Versioned, non-secret defaults for runtime and source parsing."""

    version: int
    runtime: dict[str, Any]
    parser: ParserConfig


@dataclass(frozen=True)
class ParseContext:
    """Immutable context passed to every row-producing parser component."""

    snapshot_date: str
    source_file: str = "declarations.xml"

    @property
    def snapshot(self) -> date:
        return date.fromisoformat(self.snapshot_date)


def empty_context(snapshot_date: str, source_file: str = "declarations.xml") -> ParseContext:
    """Create a context while validating the ISO snapshot-date contract."""

    date.fromisoformat(snapshot_date)
    return ParseContext(snapshot_date=snapshot_date, source_file=source_file)


__all__ = [
    "ParseContext",
    "ParserConfig",
    "PipelineConfig",
    "PipelineStatus",
    "Row",
    "TableRows",
    "TableSet",
    "empty_context",
]
