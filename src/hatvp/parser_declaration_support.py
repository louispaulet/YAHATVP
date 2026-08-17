"""Small declaration-level predicates used before row normalization."""

from __future__ import annotations

from lxml import etree


def local_name(tag: str) -> str:
    """Strip an XML namespace from a tag used by declaration predicates."""

    return tag.rsplit("}", 1)[-1]


def child_values(element: etree._Element) -> dict[str, str | None]:
    """Collect direct child text while keeping the source's empty values."""

    return {local_name(child.tag): child.text for child in element}


def income_item_has_value(item: etree._Element) -> bool:
    """Detect populated income categories without treating empty slots as rows."""

    for category in item:
        name = local_name(category.tag)
        if not name.startswith("revenuMandatItem"):
            continue
        values = child_values(category)
        if values.get("revenuElu") is not None or values.get("revenuConjoint") is not None:
            return True
    values = child_values(item)
    return values.get("totalElu") is not None or values.get("totalConjoint") is not None


def declaration_has_general(element: etree._Element) -> bool:
    return has_named_child(element, "general")


def declaration_has_income(element: etree._Element) -> bool:
    """Return whether a declaration contains the configured income section."""

    return has_named_child(element, "revenuMandatDto")


def declaration_child_names(element: etree._Element) -> tuple[str, ...]:
    """Return direct child names in source order for structural diagnostics."""

    return tuple(local_name(child.tag) for child in element)


def has_named_child(element: etree._Element, name: str) -> bool:
    """Return whether a declaration contains a direct child with this local name."""

    return name in declaration_child_names(element)


def income_category_names(item: etree._Element) -> tuple[str, ...]:
    """Return income-category names without interpreting their amounts."""

    return tuple(
        local_name(category.tag)
        for category in item
        if local_name(category.tag).startswith("revenuMandatItem")
    )


__all__ = [
    "child_values",
    "declaration_child_names",
    "declaration_has_general",
    "declaration_has_income",
    "income_item_has_value",
    "income_category_names",
    "local_name",
    "has_named_child",
]
