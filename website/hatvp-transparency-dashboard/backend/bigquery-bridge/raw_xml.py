"""Streaming extraction of one declaration from an immutable XML object."""

from __future__ import annotations

import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from lxml import etree


def local_name(tag: str) -> str:
    """Return an XML tag name without a namespace prefix."""

    return tag.rsplit("}", 1)[-1]


def declaration_uuid(element: etree._Element) -> str:
    """Read the direct UUID child without traversing private nested fields."""

    for child in element:
        if local_name(child.tag) == "uuid":
            return (child.text or "").strip()
    return ""


def iter_declaration_nodes(source: Path) -> Iterator[etree._Element]:
    """Yield declaration nodes while keeping unmatched nodes out of memory."""

    for _, element in etree.iterparse(
        str(source), events=("end",), tag=("declaration", "{*}declaration")
    ):
        yield element


def snapshot_object_name(prefix: str, snapshot_date: str) -> str:
    """Return the immutable raw XML object path for one snapshot."""

    clean_prefix = prefix.strip("/")
    return f"{clean_prefix}/raw/snapshot_date={snapshot_date}/declarations.xml"


def source_object_name(
    prefix: str, object_name: str | None, snapshot_date: str, bucket: str | None = None
) -> str:
    """Resolve a source-preserving raw object into a bucket-relative path."""

    clean_prefix = prefix.strip("/")
    clean_object = (object_name or "").strip("/")
    if not clean_object:
        return snapshot_object_name(prefix, snapshot_date)
    if clean_object.startswith("gs://"):
        uri_bucket, separator, uri_object = clean_object[5:].partition("/")
        if not separator or (bucket and uri_bucket != bucket):
            raise ValueError("Raw source URI does not match the configured bucket")
        clean_object = uri_object.strip("/")
    if ".." in Path(clean_object).parts:
        raise ValueError("Raw source object cannot contain parent traversal")
    if clean_object.startswith(f"{clean_prefix}/"):
        return clean_object
    if clean_object.startswith("raw/"):
        return f"{clean_prefix}/{clean_object}"
    raise ValueError("Raw source object must be a raw artifact path")


def download_snapshot(storage_factory: Any, bucket: str, object_name: str, target: str) -> None:
    """Download a raw object to a temporary path using the injected client factory."""

    storage_factory().bucket(bucket).blob(object_name).download_to_filename(target)


def find_declaration(source: Path, identifier: str) -> str:
    """Serialize the first declaration node whose UUID equals the identifier."""

    for element in iter_declaration_nodes(source):
        if declaration_uuid(element) == identifier:
            return etree.tostring(element, encoding="unicode")
        element.clear()
    raise LookupError("Declaration XML node not found")


def read_declaration_xml(
    storage_factory: Any,
    bucket: str,
    prefix: str,
    snapshot_date: str,
    identifier: str,
    object_name: str | None = None,
) -> str:
    """Download and stream-extract one source declaration XML node."""

    object_name = source_object_name(prefix, object_name, snapshot_date, bucket)
    with tempfile.NamedTemporaryFile(suffix=".xml") as source:
        download_snapshot(storage_factory, bucket, object_name, source.name)
        return find_declaration(Path(source.name), identifier)


__all__ = [
    "declaration_uuid",
    "find_declaration",
    "iter_declaration_nodes",
    "local_name",
    "read_declaration_xml",
    "source_object_name",
    "snapshot_object_name",
]
