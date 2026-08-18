"""Namespace-safe XML helpers shared by HATVP section parsers."""

from __future__ import annotations

import json
from typing import Any

from lxml import etree

from .normalize import normalize_text, parse_date, raw_text


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child(element: etree._Element | None, name: str) -> etree._Element | None:
    if element is None:
        return None
    return next((item for item in element if local_name(item.tag) == name), None)


def children(element: etree._Element | None, name: str) -> list[etree._Element]:
    return [item for item in element if local_name(item.tag) == name] if element is not None else []


def raw_child_text(element: etree._Element | None, name: str) -> str | None:
    item = child(element, name)
    return raw_text(item.text if item is not None else None)


def normalized_child_text(element: etree._Element | None, name: str) -> str | None:
    item = child(element, name)
    return normalize_text(item.text if item is not None else None)


def item_groups(section: etree._Element | None) -> list[etree._Element]:
    container = child(section, "items")
    if container is None:
        return []
    nested = children(container, "items")
    if nested:
        return [item for item in nested if len(item) or raw_text(item.text) is not None]
    return [container] if len(container) or raw_text(container.text) is not None else []


def flatten_leaf_values(element: etree._Element, prefix: str = "") -> dict[str, str | None]:
    if not len(element):
        return {prefix or local_name(element.tag): raw_text(element.text)}
    values: dict[str, str | None] = {}
    for item in element:
        name = local_name(item.tag)
        item_prefix = name if not prefix or name == "items" else f"{prefix}_{name}"
        values.update(flatten_leaf_values(item, item_prefix))
    return values


def first_value(values: dict[str, str | None], *names: str) -> str | None:
    return next((values.get(name) for name in names if values.get(name) is not None), None)


def first_key_containing(values: dict[str, str | None], *parts: str) -> str | None:
    return next(
        (
            value
            for key, value in values.items()
            if value is not None and all(part.casefold() in key.casefold() for part in parts)
        ),
        None,
    )


def date_fields(values: dict[str, str | None], field: str) -> tuple[str | None, str | None]:
    raw = values.get(field)
    return raw, parse_date(raw)


def raw_record(values: dict[str, Any]) -> str:
    return json.dumps(values, ensure_ascii=False, sort_keys=True, default=str)


def element_record(element: etree._Element | None) -> str | None:
    return raw_record(_element_value(element)) if element is not None else None


def _element_value(element: etree._Element) -> Any:
    if not len(element):
        return raw_text(element.text)
    values: dict[str, Any] = {}
    for child_element in element:
        name = local_name(child_element.tag)
        value = _element_value(child_element)
        if name not in values:
            values[name] = value
        elif isinstance(values[name], list):
            values[name].append(value)
        else:
            values[name] = [values[name], value]
    return values
