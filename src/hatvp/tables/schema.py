"""Stable Polars schemas for normalized Bronze Parquet outputs."""

from __future__ import annotations

import polars as pl


def _typed(names: str, dtype: object) -> dict[str, object]:
    return {name: dtype for name in names.split()}


BRONZE_PROVENANCE_SCHEMA = {
    **_typed(
        "bronze_record_key source_record_id ingestion_source source_format source_file source_url "
        "source_object source_sha256 source_ingestion_snapshot_date source_location "
        "pipeline_version "
        "parser_version raw_record_json "
        "declaration_version declaration_modificative",
        pl.String,
    ),
    "source_snapshot_date": pl.Date,
}


def _bronze(fields: dict[str, object]) -> dict[str, object]:
    return {**BRONZE_PROVENANCE_SCHEMA, **fields}


PARQUET_SCHEMAS = {
    "declarations": _bronze(
        {
            **_typed(
                "declaration_uuid source_file date_depot_raw date_depot origine complete "
                "declaration_version declaration_type_id declaration_type_label mandat_label "
                "mandat_type mandat_category_code mandat_category_label mandat_file_type "
                "mandat_type_label organ_code organ_code_list organ_label "
                "organ_declaration_label organ_parent quality_declarant quality_declarant_pdf "
                "date_debut_mandat_raw date_debut_mandat date_fin_mandat_raw date_fin_mandat "
                "date_derniere_declaration_raw declaration_modificative quality_status "
                "quality_reason",
                pl.String,
            ),
            "snapshot_date": pl.Date,
            "income_section_present": pl.Boolean,
            "income_section_populated_item_count": pl.Int64,
        }
    ),
    "people": _bronze(
        {
            **_typed(
                "declaration_uuid source_file civilite gender nom prenom email date_naissance_raw "
                "date_naissance telephone_dec adresse_voie adresse_complement "
                "date_naissance_quality_status date_naissance_quality_reason "
                "adresse_code_postal adresse_ville adresse_pays quality_status quality_reason",
                pl.String,
            ),
            "date_naissance_date": pl.Date,
            "date_naissance_year": pl.Int64,
            "snapshot_date": pl.Date,
        }
    ),
    "incomes": _bronze(
        {
            **_typed(
                "declaration_uuid source_section income_stream income_year income_type raw_value "
                "quality_status quality_reason raw_record_json",
                pl.String,
            ),
            **{
                name: pl.Int64
                for name in ("source_item_index", "income_category_index", "remuneration_index")
            },
            **{name: pl.Float64 for name in ("normalized_value", "spouse_normalized_value")},
            "snapshot_date": pl.Date,
            "spouse_raw_value": pl.String,
        }
    ),
    "assets": _bronze(
        {
            **_typed(
                "declaration_uuid source_section asset_name raw_value quality_status "
                "quality_reason asset_acquisition_year_raw asset_event_precision "
                "asset_event_source_field raw_record_json",
                pl.String,
            ),
            "source_item_index": pl.Int64,
            "asset_acquisition_year": pl.Int64,
            "asset_event_date": pl.Date,
            "normalized_value": pl.Float64,
            "snapshot_date": pl.Date,
        }
    ),
}


def schema_for(table_name: str) -> dict[str, object]:
    """Return a copy of the stable schema for a known normalized table."""

    return dict(PARQUET_SCHEMAS.get(table_name, {}))
