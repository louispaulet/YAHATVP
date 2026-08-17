"""Runtime settings and packaged schema configuration."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .models import ParserConfig, PipelineConfig


def _load_document(path: Path | None = None) -> dict[str, Any]:
    source = (
        path.read_text(encoding="utf-8")
        if path
        else files("hatvp").joinpath("pipeline.yml").read_text(encoding="utf-8")
    )
    document = yaml.safe_load(source)
    if not isinstance(document, dict) or document.get("version") != 1:
        raise ValueError("pipeline.yml must contain version 1")
    return document


def load_pipeline_config(path: Path | None = None) -> PipelineConfig:
    """Load and validate the versioned YAML defaults used by the pipeline."""

    document = _load_document(path)
    parser = document.get("parser") or {}
    csv_config = parser.get("csv") or {}
    candidates = parser.get("field_candidates") or {}
    parser_config = ParserConfig(
        xml_root=str(parser.get("xml_root")),
        allowed_top_level_children=tuple(parser.get("allowed_top_level_children", ())),
        sections=dict(parser.get("sections") or {}),
        field_candidates={key: tuple(values) for key, values in candidates.items()},
        csv_delimiter=str(csv_config.get("delimiter", ";")),
        csv_identity_columns=tuple(csv_config.get("identity_columns", ())),
    )
    if not parser_config.xml_root or not parser_config.csv_identity_columns:
        raise ValueError("pipeline.yml is missing parser identity configuration")
    return PipelineConfig(
        int(document["version"]), dict(document.get("runtime") or {}), parser_config
    )


_DEFAULTS = load_pipeline_config().runtime


class Settings(BaseSettings):
    """YAML defaults overridden by environment variables and CLI values."""

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False, extra="ignore")

    hatvp_bucket: str | None = None
    hatvp_prefix: str = _DEFAULTS["hatvp_prefix"]
    hatvp_xml_url: str = _DEFAULTS["hatvp_xml_url"]
    hatvp_csv_url: str = _DEFAULTS["hatvp_csv_url"]
    hatvp_enable_bigquery: bool = False
    hatvp_bigquery_project: str | None = None
    hatvp_bigquery_dataset: str = _DEFAULTS["hatvp_bigquery_dataset"]
    hatvp_bigquery_location: str = _DEFAULTS["hatvp_bigquery_location"]
    local_output: Path | None = None
    pipeline_version: str = _DEFAULTS["pipeline_version"]
    pipeline_git_sha: str = "unknown"
    user_agent: str = _DEFAULTS["user_agent"]
    download_connect_timeout_seconds: float = Field(
        default=_DEFAULTS["download_connect_timeout_seconds"], gt=0
    )
    download_read_timeout_seconds: float = Field(
        default=_DEFAULTS["download_read_timeout_seconds"], gt=0
    )
    download_retries: int = Field(default=_DEFAULTS["download_retries"], ge=1, le=8)

    def validate_storage(self) -> None:
        if self.local_output is None and not self.hatvp_bucket:
            raise ValueError("Set HATVP_BUCKET for GCS mode or use --local-output for local mode")

    @property
    def bigquery_project(self) -> str | None:
        return self.hatvp_bigquery_project or self.hatvp_bucket


__all__ = ["Settings", "load_pipeline_config"]
