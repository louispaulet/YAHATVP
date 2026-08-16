import json
import shutil
from pathlib import Path

import pytest

from hatvp.config import Settings
from hatvp.download import DownloadedFile
from hatvp.main import run_pipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _fixture_downloader(url: str, name: str, destination: Path, **_: object) -> DownloadedFile:
    source = FIXTURES / ("liste.csv" if name == "liste.csv" else "declarations.xml")
    shutil.copyfile(source, destination)
    from hatvp.hashing import sha256_file

    return DownloadedFile(
        name=name,
        url=url,
        path=destination,
        size_bytes=destination.stat().st_size,
        sha256=sha256_file(destination),
        elapsed_seconds=0.001,
    )


def _settings(output: Path) -> Settings:
    return Settings(
        local_output=output,
        hatvp_xml_url="fixture://declarations.xml",
        hatvp_csv_url="fixture://liste.csv",
    )


def test_unchanged_snapshot_detection(tmp_path: Path) -> None:
    output = tmp_path / "output"
    assert (
        run_pipeline(_settings(output), downloader=_fixture_downloader) == "SUCCESS_WITH_WARNINGS"
    )
    state_path = output / "hatvp" / "state/latest.json"
    first_state = json.loads(state_path.read_text())

    assert run_pipeline(_settings(output), downloader=_fixture_downloader) == "NO_CHANGE"
    assert json.loads(state_path.read_text()) == first_state


def test_dry_run_does_not_write_local_outputs(tmp_path: Path) -> None:
    output = tmp_path / "output"

    assert (
        run_pipeline(_settings(output), dry_run=True, downloader=_fixture_downloader)
        == "SUCCESS_WITH_WARNINGS"
    )
    assert not output.exists()


def test_state_is_not_updated_after_pipeline_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "output"

    def broken_downloader(url: str, name: str, destination: Path, **_: object) -> DownloadedFile:
        source = FIXTURES / ("liste.csv" if name == "liste.csv" else "malformed.xml")
        shutil.copyfile(source, destination)
        from hatvp.hashing import sha256_file

        return DownloadedFile(
            name=name,
            url=url,
            path=destination,
            size_bytes=destination.stat().st_size,
            sha256=sha256_file(destination),
            elapsed_seconds=0.001,
        )

    with pytest.raises(ValueError, match="malformed"):
        run_pipeline(_settings(output), downloader=broken_downloader)

    with pytest.raises(ValueError, match="malformed"):
        run_pipeline(_settings(output), downloader=broken_downloader)

    assert not (output / "hatvp" / "state/latest.json").exists()
