"""Small declaration-level predicates used before row normalization."""

from __future__ import annotations

from lxml import etree


def income_item_has_value(item: etree._Element) -> bool:
    """Detect populated income categories without treating empty slots as rows."""

    for category in item:
        name = category.tag.rsplit("}", 1)[-1]
        if not name.startswith("revenuMandatItem"):
            continue
        values = {child.tag.rsplit("}", 1)[-1]: child.text for child in category}
        if values.get("revenuElu") is not None or values.get("revenuConjoint") is not None:
            return True
    values = {child.tag.rsplit("}", 1)[-1]: child.text for child in item}
    return values.get("totalElu") is not None or values.get("totalConjoint") is not None


def declaration_has_general(element: etree._Element) -> bool:
    return any(child.tag.rsplit("}", 1)[-1] == "general" for child in element)


__all__ = ["declaration_has_general", "income_item_has_value"]
