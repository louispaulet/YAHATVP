"""Stable Polars schemas for curated Parquet outputs."""

from __future__ import annotations

import polars as pl


def _strings(names: str) -> dict[str, object]:
    return {name for name in names.split()}


PARQUET_SCHEMAS = {
    "declarations": {
        **{
            name: pl.String
            for name in _strings(
                "declaration_uuid source_file date_depot_raw date_depot origine complete "
                "declaration_version declaration_type_id declaration_type_label mandat_label "
                "mandat_type mandat_category_code mandat_category_label mandat_file_type "
                "mandat_type_label organ_code organ_code_list organ_label "
                "organ_declaration_label organ_parent quality_declarant quality_declarant_pdf "
                "date_debut_mandat_raw date_debut_mandat date_fin_mandat_raw date_fin_mandat "
                "date_derniere_declaration_raw declaration_modificative quality_status "
                "quality_reason"
            )
        },
        "snapshot_date": pl.Date,
        "income_section_present": pl.Boolean,
        "income_section_populated_item_count": pl.Int64,
    },
    "people": {
        **{
            name: pl.String
            for name in _strings(
                "declaration_uuid source_file civilite nom prenom email date_naissance_raw "
                "date_naissance telephone_dec adresse_voie adresse_complement "
                "adresse_code_postal adresse_ville adresse_pays quality_status quality_reason"
            )
        },
        "snapshot_date": pl.Date,
    },
    "incomes": {
        **{
            name: pl.String
            for name in _strings(
                "declaration_uuid source_section income_stream income_year income_type raw_value "
                "quality_status quality_reason raw_record_json"
            )
        },
        **{
            name: pl.Int64
            for name in ("source_item_index", "income_category_index", "remuneration_index")
        },
        **{name: pl.Float64 for name in ("normalized_value", "spouse_normalized_value")},
        "snapshot_date": pl.Date,
        "spouse_raw_value": pl.String,
    },
    "assets": {
        **{
            name: pl.String
            for name in (
                "declaration_uuid",
                "source_section",
                "asset_name",
                "raw_value",
                "quality_status",
                "quality_reason",
                "raw_record_json",
            )
        },
        "source_item_index": pl.Int64,
        "normalized_value": pl.Float64,
        "snapshot_date": pl.Date,
    },
}


def schema_for(table_name: str) -> dict[str, object]:
    """Return a copy of the stable schema for a known curated table."""

    return dict(PARQUET_SCHEMAS.get(table_name, {}))


__all__ = ["PARQUET_SCHEMAS", "schema_for"]
