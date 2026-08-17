"""Fixture-backed test package shared by focused parser and pipeline modules."""

from __future__ import annotations

from pathlib import Path

TEST_ROOT = Path(__file__).parent
FIXTURES = TEST_ROOT / "fixtures"
SNAPSHOT_DATE = "2026-08-16"


def fixture_path(name: str) -> Path:
    """Return a fixture path without allowing callers to escape the fixture root."""

    path = (FIXTURES / name).resolve()
    if path.parent != FIXTURES.resolve():
        raise ValueError(f"Fixture path must be a direct child: {name}")
    return path


def fixture_bytes(name: str) -> bytes:
    """Read immutable fixture bytes for exact-source assertions."""

    return fixture_path(name).read_bytes()


def fixture_text(name: str) -> str:
    """Read a UTF-8 fixture for small configuration and listing assertions."""

    return fixture_path(name).read_text(encoding="utf-8")


def fixture_exists(name: str) -> bool:
    """Return whether a named fixture is present in the repository."""

    return fixture_path(name).exists()


def snapshot_value() -> str:
    """Return the shared fixture snapshot used by normalized row tests."""

    return SNAPSHOT_DATE


def fixture_names() -> tuple[str, ...]:
    """Return direct fixture names in deterministic filesystem order."""

    return tuple(sorted(path.name for path in FIXTURES.iterdir() if path.is_file()))


def assert_fixture(name: str, suffix: str) -> Path:
    """Resolve and validate a fixture extension at the test boundary."""

    path = fixture_path(name)
    if path.suffix != suffix:
        raise AssertionError(f"Expected {suffix} fixture, received {name}")
    return path


__all__ = [
    "FIXTURES",
    "SNAPSHOT_DATE",
    "TEST_ROOT",
    "assert_fixture",
    "fixture_bytes",
    "fixture_exists",
    "fixture_names",
    "fixture_path",
    "fixture_text",
    "snapshot_value",
]
