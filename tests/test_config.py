"""YAML defaults, environment precedence, and typed parser configuration tests."""

from pathlib import Path

import pytest

from hatvp.config import Settings, load_pipeline_config
from hatvp.parser import parser_config


def test_packaged_yaml_provides_runtime_and_parser_defaults() -> None:
    config = load_pipeline_config()

    assert config.version == 1
    assert config.runtime_value("hatvp_prefix") == "hatvp"
    assert config.runtime_value("download_retries") >= 1
    assert config.runtime_value("person_dob_max_age_years") == 100
    assert config.parser.xml_root == "declarations"
    assert config.parser.csv_delimiter == ";"
    assert "declaration" in config.parser.allowed_top_level_children
    assert config.parser.section("assets")


def test_settings_environment_overrides_packaged_yaml(monkeypatch) -> None:
    monkeypatch.setenv("HATVP_PREFIX", "fixture-prefix")
    monkeypatch.setenv("DOWNLOAD_RETRIES", "4")
    monkeypatch.setenv("HATVP_ENABLE_BIGQUERY", "true")
    monkeypatch.setenv("HATVP_PERSON_DOB_MAX_AGE_YEARS", "90")

    settings = Settings()

    assert settings.hatvp_prefix == "fixture-prefix"
    assert settings.download_retries == 4
    assert settings.hatvp_enable_bigquery is True
    assert settings.hatvp_person_dob_max_age_years == 90


def test_cli_style_model_copy_has_highest_precedence(monkeypatch) -> None:
    monkeypatch.delenv("HATVP_BUCKET", raising=False)
    settings = Settings(hatvp_prefix="yaml-or-env")
    overridden = settings.model_copy(update={"hatvp_prefix": "cli-prefix"})

    assert overridden.hatvp_prefix == "cli-prefix"
    assert overridden.bigquery_project is None


def test_parser_configuration_is_the_same_typed_object_used_by_parser() -> None:
    config = load_pipeline_config().parser

    assert parser_config() == config
    assert config.candidates("asset_value")
    assert config.candidates("missing") == ()
    assert config.csv_identity_columns


def test_custom_yaml_requires_version_and_identity_configuration(tmp_path: Path) -> None:
    invalid_version = tmp_path / "invalid-version.yml"
    invalid_version.write_text("version: 2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="version 1"):
        load_pipeline_config(invalid_version)

    invalid_parser = tmp_path / "invalid-parser.yml"
    invalid_parser.write_text("version: 1\nparser:\n  xml_root: declarations\n", encoding="utf-8")
    with pytest.raises(ValueError, match="identity configuration"):
        load_pipeline_config(invalid_parser)


def test_storage_validation_requires_bucket_or_local_output(monkeypatch) -> None:
    monkeypatch.delenv("HATVP_BUCKET", raising=False)
    with pytest.raises(ValueError, match="HATVP_BUCKET"):
        Settings().validate_storage()
    Settings(local_output=Path("/tmp/hatvp-fixture")).validate_storage()


def test_typed_settings_keep_positive_timeout_and_retry_constraints() -> None:
    settings = Settings(download_connect_timeout_seconds=2.5, download_retries=3)

    assert settings.download_connect_timeout_seconds == 2.5
    assert settings.download_retries == 3
