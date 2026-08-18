"""Parameterized full-text search query for public declaration metadata."""

from __future__ import annotations

from query_support import (
    SEARCH_LIMIT,
    any_predicates,
    dataset_prefix,
)
from search_fields import (
    ASSET_FIELDS,
    DECLARATION_FIELDS,
    INCOME_FIELDS,
    child_match,
    string_predicates,
)


def build_search_query(project: str, dataset: str) -> str:
    """Build a parameterized search over public Gold declaration fields."""

    prefix = dataset_prefix(project, dataset)
    declaration_match = any_predicates(string_predicates(DECLARATION_FIELDS))
    searchable = "\n      ".join(
        [
            declaration_match,
            child_match("incomes", "i", INCOME_FIELDS).format(prefix=prefix),
            child_match("assets", "a", ASSET_FIELDS).format(prefix=prefix),
        ]
    )
    return f"""WITH latest AS (
  SELECT MAX(snapshot_date) AS snapshot_date FROM {prefix}.gold_declarations
),
search AS (
  SELECT NORMALIZE_AND_CASEFOLD(@search_term) AS term
),
matched AS (
  SELECT DISTINCT
    d.declaration_uuid, p.civilite, p.prenom, p.nom,
    d.declaration_type_label, d.mandat_label, d.mandat_type_label,
    d.mandat_category_label, d.organ_label, d.organ_declaration_label,
    d.date_depot, d.declaration_modificative
  FROM {prefix}.gold_declarations d
  CROSS JOIN latest l
  CROSS JOIN search s
  LEFT JOIN {prefix}.gold_people p
    ON p.declaration_uuid = d.declaration_uuid
    AND p.snapshot_date = d.snapshot_date
  WHERE d.snapshot_date = l.snapshot_date
    AND ({searchable})
)
SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
CURRENT_TIMESTAMP() AS generated_at,
TO_JSON_STRING(ARRAY(
  SELECT AS STRUCT declaration_uuid, civilite, prenom, nom,
    declaration_type_label, mandat_label, mandat_type_label,
    mandat_category_label, organ_label, organ_declaration_label,
    date_depot, declaration_modificative
  FROM matched
  ORDER BY date_depot DESC, nom, prenom, declaration_uuid
  LIMIT {SEARCH_LIMIT}
)) AS results_json
FROM latest l"""


def search_result_limit() -> int:
    """Return the bounded result count promised by the public search route."""

    return SEARCH_LIMIT


__all__ = ["build_search_query", "child_match", "search_result_limit", "string_predicates"]
