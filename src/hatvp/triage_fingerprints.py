"""Exact and parser-semantic XML fingerprints for duplicate review."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path
from typing import Any

from lxml import etree

from .xml_support import local_name, raw_child_text


def semantic_xml_bytes(element: etree._Element) -> bytes:
    canonical = etree.tostring(element, method="c14n", exclusive=True, with_comments=False)
    normalized = etree.fromstring(canonical)
    for node in normalized.iter():
        if node.text is not None:
            node.text = " ".join(node.text.split())
        if node.tail is not None:
            node.tail = " ".join(node.tail.split())
    return etree.tostring(normalized, method="c14n", exclusive=True, with_comments=False)


def declaration_xml_fingerprints(path: Path) -> dict[str, list[dict[str, Any]]]:
    fingerprints: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    context = etree.iterparse(
        str(path),
        events=("end",),
        recover=False,
        huge_tree=True,
        load_dtd=False,
        no_network=True,
        resolve_entities=False,
    )
    try:
        for _, element in context:
            if local_name(element.tag) != "declaration":
                continue
            uuid = raw_child_text(element, "uuid")
            if uuid:
                canonical = etree.tostring(
                    element, method="c14n", exclusive=True, with_comments=False
                )
                semantic = semantic_xml_bytes(element)
                fingerprints[uuid].append(
                    {
                        "occurrence_index": len(fingerprints[uuid]),
                        "canonical_xml_sha256": hashlib.sha256(canonical).hexdigest(),
                        "canonical_xml_bytes": len(canonical),
                        "semantic_xml_sha256": hashlib.sha256(semantic).hexdigest(),
                        "date_depot_raw": raw_child_text(element, "dateDepot"),
                    }
                )
            parent = element.getparent()
            element.clear()
            if parent is not None:
                while element.getprevious() is not None:
                    del parent[0]
    except etree.XMLSyntaxError as exc:
        raise ValueError(f"HATVP XML is malformed: {exc}") from exc
    return dict(fingerprints)


__all__ = ["declaration_xml_fingerprints", "semantic_xml_bytes"]
