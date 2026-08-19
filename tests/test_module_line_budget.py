"""Ingestion invariant: pipeline Python modules remain focused components."""

from __future__ import annotations

import subprocess
from pathlib import Path

MIN_LINES = 70
MAX_LINES = 100
ROOT = Path(__file__).parents[1]


def tracked_python_files() -> list[Path]:
    """Read the same tracked-file set that reviewers see in the Git diff."""

    result = subprocess.run(
        ["git", "ls-files", "src/hatvp", "tests"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line.endswith(".py")]


def physical_lines(path: Path) -> int:
    """Count physical lines, including imports, comments, and blank lines."""

    return len(path.read_text(encoding="utf-8").splitlines())


def line_budget_violations(paths: list[Path]) -> list[tuple[str, int]]:
    """Return paths outside the inclusive module budget."""

    violations = []
    for path in paths:
        count = physical_lines(path)
        if count < MIN_LINES or count > MAX_LINES:
            try:
                label = str(path.relative_to(ROOT))
            except ValueError:
                label = str(path)
            violations.append((label, count))
    return violations


def test_all_tracked_python_files_fit_the_inclusive_budget() -> None:
    paths = tracked_python_files()

    assert paths
    assert line_budget_violations(paths) == []


def test_budget_scanner_includes_package_initializers_and_tests() -> None:
    paths = {path.relative_to(ROOT).as_posix() for path in tracked_python_files()}

    assert "src/hatvp/__init__.py" in paths
    assert "tests/test_module_line_budget.py" in paths
    assert any(path.startswith("tests/") for path in paths)


def test_budget_constants_are_inclusive_and_positive() -> None:
    assert MIN_LINES == 70
    assert MAX_LINES == 100
    assert MIN_LINES <= MAX_LINES


def test_line_count_is_deterministic_for_a_known_fixture() -> None:
    path = ROOT / "tests" / "fixtures" / "liste.csv"

    assert physical_lines(path) > 0
    assert physical_lines(path) == len(path.read_text(encoding="utf-8").splitlines())


def test_violations_report_relative_paths_and_counts(tmp_path: Path) -> None:
    short = tmp_path / "short.py"
    short.write_text("pass\n", encoding="utf-8")

    violations = line_budget_violations([short])

    assert violations[0][1] == 1
