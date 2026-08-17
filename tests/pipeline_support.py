from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from hatvp import main as main_module
from hatvp.config import Settings
from hatvp.download import DownloadedFile
from hatvp.hashing import sha256_file

FIXTURES = Path(__file__).parent / "fixtures"


def downloader_for(
    *,
    xml_source: Path = FIXTURES / "declarations.xml",
    csv_source: Path = FIXTURES / "liste.csv",
):
    def downloader(url: str, name: str, destination: Path, **_: object) -> DownloadedFile:
        source = csv_source if name == "liste.csv" else xml_source
        shutil.copyfile(source, destination)
        return DownloadedFile(
            name=name,
            url=url,
            path=destination,
            size_bytes=destination.stat().st_size,
            sha256=sha256_file(destination),
            elapsed_seconds=0.001,
        )

    return downloader


def fixture_downloader(url: str, name: str, destination: Path, **_: object) -> DownloadedFile:
    return downloader_for()(url, name, destination)


def changed_fixture(source: Path, destination: Path, old: bytes, new: bytes) -> Path:
    content = source.read_bytes()
    assert old in content
    destination.write_bytes(content.replace(old, new, 1))
    return destination


def settings(output: Path) -> Settings:
    return Settings(
        local_output=output,
        hatvp_xml_url="fixture://declarations.xml",
        hatvp_csv_url="fixture://liste.csv",
    )


def settings_with_bigquery(output: Path) -> Settings:
    return settings(output).model_copy(
        update={"hatvp_enable_bigquery": True, "hatvp_bigquery_project": "fixture-project"}
    )


def state_path(output: Path) -> Path:
    return output / "hatvp" / "state/latest.json"


def raw_path(output: Path, snapshot_date: str, name: str) -> Path:
    return output / "hatvp" / f"raw/snapshot_date={snapshot_date}/{name}"


def warning_status(status: str) -> None:
    assert status == "SUCCESS_WITH_WARNINGS"


def json_events(stderr: str) -> list[dict]:
    return [json.loads(line) for line in stderr.splitlines() if line.startswith("{")]


def cli_with_fixture(
    monkeypatch: pytest.MonkeyPatch,
    output: Path,
    *,
    xml_source: Path = FIXTURES / "declarations.xml",
    csv_source: Path = FIXTURES / "liste.csv",
) -> int:
    real_run_pipeline = main_module.run_pipeline

    def fixture_run_pipeline(
        configured: Settings, *, dry_run: bool = False, force: bool = False
    ) -> str:
        return real_run_pipeline(
            configured,
            dry_run=dry_run,
            force=force,
            downloader=downloader_for(xml_source=xml_source, csv_source=csv_source),
        )

    monkeypatch.setattr(main_module, "run_pipeline", fixture_run_pipeline)
    return main_module.cli(["--local-output", str(output)])
