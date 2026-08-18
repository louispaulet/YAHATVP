"""Fixed public field inventories used by declaration search."""

from __future__ import annotations

from query_support import exists_text_match, normalized_contains

DECLARATION_FIELDS = (
    "p.civilite",
    "p.nom",
    "p.prenom",
    "d.declaration_uuid",
    "d.source_file",
    "d.date_depot",
    "d.origine",
    "d.declaration_version",
    "d.declaration_type_id",
    "d.declaration_type_label",
    "d.mandat_label",
    "d.mandat_type",
    "d.mandat_category_code",
    "d.mandat_category_label",
    "d.mandat_file_type",
    "d.mandat_type_label",
    "d.organ_code",
    "d.organ_code_list",
    "d.organ_label",
    "d.organ_declaration_label",
    "d.organ_parent",
    "d.quality_declarant",
    "d.quality_declarant_pdf",
    "d.date_debut_mandat_raw",
    "d.date_debut_mandat",
    "d.date_fin_mandat_raw",
    "d.date_fin_mandat",
    "d.date_derniere_declaration_raw",
    "d.declaration_modificative",
)
INCOME_FIELDS = (
    "i.source_section",
    "i.income_stream",
    "i.income_year",
    "i.income_type",
    "i.raw_value",
)
ASSET_FIELDS = ("a.source_section", "a.asset_name", "a.raw_value")


def string_predicates(fields: tuple[str, ...]) -> list[str]:
    """Build normalized substring predicates for a fixed field inventory."""

    return [normalized_contains(field) for field in fields]


def numeric_predicates(alias: str) -> list[str]:
    """Allow searching the normalized amount without exposing the amount table."""

    return [f"STRPOS(CAST({alias}.normalized_value AS STRING), s.term) > 0"]


def child_match(table_name: str, alias: str, fields: tuple[str, ...]) -> str:
    """Build one child-table existence check with its fixed amount predicate."""

    return exists_text_match(
        table_name, alias, string_predicates(fields) + numeric_predicates(alias)
    )


def public_search_fields() -> tuple[str, ...]:
    """Return the declaration fields searched by the public endpoint."""

    return DECLARATION_FIELDS + INCOME_FIELDS + ASSET_FIELDS


__all__ = [
    "ASSET_FIELDS",
    "DECLARATION_FIELDS",
    "INCOME_FIELDS",
    "child_match",
    "public_search_fields",
    "string_predicates",
]
