"""Bronze row identity and source-provenance helpers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

from ..models import ParseContext, Row

PARSER_VERSION = "1"


def context_for(
    snapshot_date: str,
    source_file: str,
    source_format: str,
    default_object: str,
    metadata: Mapping[str, Any] | None = None,
) -> ParseContext:
    """Build a parser context from optional download and archive metadata."""

    values = metadata or {}
    return ParseContext(
        snapshot_date=snapshot_date,
        source_file=source_file,
        source_format=source_format,
        source_url=values.get("url"),
        source_object=values.get("source_object") or default_object,
        source_sha256=values.get("sha256"),
        pipeline_version=values.get("pipeline_version"),
        parser_version=str(values.get("parser_version") or PARSER_VERSION),
    )


def record_key(context: ParseContext, source_record_id: str | None, row_index: int) -> str:
    """Return a deterministic key for one source-record occurrence."""

    identity = source_record_id or f"row-{row_index}"
    material = "|".join(
        (
            context.source_format,
            context.source_file,
            context.snapshot_date,
            identity,
            str(row_index),
        )
    )
    return f"bronze_{hashlib.sha256(material.encode()).hexdigest()[:32]}"


def source_location(row: Row, base: str) -> str:
    """Describe a normalized row's source path without inventing source fields."""

    section = row.get("source_section")
    if not section:
        return base
    index = row.get("source_item_index")
    suffix = f"/{section}[item={index}]" if index is not None else f"/{section}"
    return f"{base}{suffix}"


def apply_provenance(
    row: Row,
    context: ParseContext,
    key: str,
    source_record_id: str | None,
    location: str,
) -> Row:
    """Attach immutable source and version metadata to one Bronze row."""

    row.update(
        {
            "bronze_record_key": key,
            "source_record_id": source_record_id,
            "source_snapshot_date": context.snapshot_date,
            "source_format": context.source_format,
            "source_file": context.source_file,
            "source_url": context.source_url,
            "source_object": context.source_object,
            "source_sha256": context.source_sha256,
            "source_location": location,
            "pipeline_version": context.pipeline_version,
            "parser_version": context.parser_version,
        }
    )
    if context.declaration_version is not None:
        row["declaration_version"] = context.declaration_version
    if context.declaration_modificative is not None:
        row["declaration_modificative"] = context.declaration_modificative
    return row


__all__ = ["PARSER_VERSION", "apply_provenance", "context_for", "record_key", "source_location"]
