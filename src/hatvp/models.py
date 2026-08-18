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

    def section(self, name: str) -> str:
        """Return a configured XML section name with a useful error."""

        try:
            return str(self.sections[name])
        except KeyError as exc:
            raise KeyError(f"Unknown parser section: {name}") from exc

    def candidates(self, name: str) -> tuple[str, ...]:
        """Return configured field candidates for a parser component."""

        return self.field_candidates.get(name, ())


@dataclass(frozen=True)
class PipelineConfig:
    """Versioned, non-secret defaults for runtime and source parsing."""

    version: int
    runtime: dict[str, Any]
    parser: ParserConfig

    def runtime_value(self, name: str, default: Any = None) -> Any:
        """Read one typed-runtime default without exposing the raw YAML mapping."""

        return self.runtime.get(name, default)


@dataclass(frozen=True)
class ParseContext:
    """Immutable context passed to every row-producing parser component."""

    snapshot_date: str
    source_file: str = "declarations.xml"
    source_format: str = "xml"
    source_url: str | None = None
    source_object: str | None = None
    source_sha256: str | None = None
    pipeline_version: str | None = None
    parser_version: str = "1"
    declaration_version: str | None = None
    declaration_modificative: str | None = None

    @property
    def snapshot(self) -> date:
        return date.fromisoformat(self.snapshot_date)

    @property
    def source_label(self) -> str:
        """Return the source file label carried into normalized provenance."""

        return self.source_file


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
