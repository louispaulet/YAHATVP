"""Income category parser and compatibility exports."""

from __future__ import annotations

from typing import Any

from lxml import etree

from .models import ParseContext, ParserConfig
from .normalize import normalize_text
from .parser_income_fields import income_row, is_populated
from .parser_mandate_income import mandate_income_rows
from .xml_support import child, flatten_leaf_values, item_groups, normalized_child_text, raw_record


def income_rows(
    element: etree._Element, context: ParseContext, config: ParserConfig
) -> list[dict[str, Any]]:
    uuid = normalized_child_text(element, "uuid")
    section = child(element, config.sections["income"])
    rows: list[dict[str, Any]] = []
    for item_index, item in enumerate(item_groups(section)):
        values = flatten_leaf_values(item)
        year = normalize_text(values.get("annee"))
        categories = [
            node for node in item if node.tag.rsplit("}", 1)[-1].startswith("revenuMandatItem")
        ]
        populated = 0
        for category_index, category in enumerate(categories):
            category_values = flatten_leaf_values(category)
            raw_value = category_values.get("revenuElu")
            spouse_raw = category_values.get("revenuConjoint")
            if not is_populated(raw_value, spouse_raw):
                continue
            populated += 1
            rows.append(
                income_row(
                    uuid,
                    context,
                    item_index,
                    category_index,
                    year,
                    category_values,
                    raw_value,
                    spouse_raw,
                    raw_record(category_values),
                )
            )
        if populated == 0 and is_populated(values.get("totalElu"), values.get("totalConjoint")):
            rows.append(
                income_row(
                    uuid,
                    context,
                    item_index,
                    None,
                    year,
                    values,
                    values.get("totalElu"),
                    values.get("totalConjoint"),
                    raw_record(values),
                    income_type="totalElu",
                )
            )
    return rows


def income_row_count(rows: list[dict[str, Any]]) -> int:
    """Count normalized declared-income rows for coverage diagnostics."""

    return len([row for row in rows if row.get("income_stream") == "revenu_mandat"])


__all__ = ["income_row_count", "income_rows", "is_populated", "mandate_income_rows"]
