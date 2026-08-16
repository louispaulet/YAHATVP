from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    hatvp_bucket: str | None = None
    hatvp_prefix: str = "hatvp"
    hatvp_xml_url: str = "https://www.hatvp.fr/livraison/merge/declarations.xml"
    hatvp_csv_url: str = "https://www.hatvp.fr/livraison/opendata/liste.csv"
    hatvp_enable_bigquery: bool = False
    hatvp_bigquery_project: str | None = None
    hatvp_bigquery_dataset: str = "hatvp"

    local_output: Path | None = None
    pipeline_version: str = "0.1.0"
    pipeline_git_sha: str = "unknown"
    user_agent: str = "YAHATVP-ingestion/0.1 (+https://github.com/louispaulet/YAHATVP)"
    download_connect_timeout_seconds: float = Field(default=15.0, gt=0)
    download_read_timeout_seconds: float = Field(default=180.0, gt=0)
    download_retries: int = Field(default=3, ge=1, le=8)

    def validate_storage(self) -> None:
        if self.local_output is None and not self.hatvp_bucket:
            raise ValueError("Set HATVP_BUCKET for GCS mode or use --local-output for local mode")

    @property
    def bigquery_project(self) -> str | None:
        return self.hatvp_bigquery_project or self.hatvp_bucket
