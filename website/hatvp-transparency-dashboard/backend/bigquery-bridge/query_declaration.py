"""Single-declaration metadata query for the dashboard source viewer."""

from __future__ import annotations

from query_support import dataset_prefix

DECLARATION_FIELDS = (
    "d.declaration_uuid AS declaration_uuid",
    "p.civilite AS civilite",
    "p.prenom AS prenom",
    "p.nom AS nom",
    "d.declaration_type_label AS declaration_type_label",
    "d.mandat_label AS mandat_label",
    "d.mandat_type_label AS mandat_type_label",
    "d.mandat_category_label AS mandat_category_label",
    "d.organ_label AS organ_label",
    "d.organ_declaration_label AS organ_declaration_label",
    "d.date_depot AS date_depot",
    "d.declaration_modificative AS declaration_modificative",
)


def declaration_struct() -> str:
    """Return the explicit public metadata projection used in JSON output."""

    return ",\n  ".join(DECLARATION_FIELDS)


def build_declaration_query(project: str, dataset: str) -> str:
    """Build a parameterized lookup for one public declaration's metadata."""

    prefix = dataset_prefix(project, dataset)
    fields = declaration_struct()
    return f"""WITH latest AS (
  SELECT MAX(snapshot_date) AS snapshot_date FROM {prefix}.declarations
)
SELECT FORMAT_DATE('%Y-%m-%d', l.snapshot_date) AS snapshot_date,
CURRENT_TIMESTAMP() AS generated_at,
TO_JSON_STRING(STRUCT(
  {fields}
)) AS result_json
FROM latest l
JOIN {prefix}.declarations d ON d.snapshot_date = l.snapshot_date
LEFT JOIN {prefix}.people p
  ON p.declaration_uuid = d.declaration_uuid
  AND p.snapshot_date = d.snapshot_date
WHERE d.declaration_uuid = @declaration_uuid
LIMIT 1"""


def declaration_query_fields() -> tuple[str, ...]:
    """Expose the selected field inventory for contract-focused tests."""

    return DECLARATION_FIELDS


def declaration_field_aliases() -> tuple[str, ...]:
    """Return the JSON aliases without permitting caller-defined projections."""

    return tuple(field.rsplit(" AS ", 1)[-1] for field in DECLARATION_FIELDS)


def public_declaration_field_count() -> int:
    """Return the count of explicitly selected, non-contact metadata fields."""

    return len(DECLARATION_FIELDS)


__all__ = [
    "DECLARATION_FIELDS",
    "build_declaration_query",
    "declaration_query_fields",
    "declaration_field_aliases",
    "public_declaration_field_count",
    "declaration_struct",
]
