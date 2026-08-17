"""Command-line entry point for source-linked quality triage.

The triage implementation lives in :mod:`hatvp.triage` so its functions can
also be imported by fixture tests and operational helpers.  Python executes a
package's ``__main__`` module when the package is invoked with ``-m``; this
small adapter keeps that invocation explicit and easy to discover.

The command reads an existing artifact snapshot, builds source-linked review
evidence, and writes JSON and Markdown reports.  It does not run ingestion,
change raw objects, or advance pipeline state.

Callers select either a local artifact root or a GCS bucket through the
arguments defined by the façade.  The return code is zero after both review
artifacts are written successfully.  Argument parsing and report assembly
remain in one place so the importable API and module invocation cannot drift.

This adapter intentionally contains no storage, parsing, or report logic.  Its
only responsibility is translating Python's module invocation into the same
typed call used by tests and operational wrappers.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import NoReturn

from . import main as _run_review


def _copy_arguments(argv: Sequence[str] | None) -> list[str] | None:
    """Make an explicit list for the package façade's argparse boundary."""

    if argv is None:
        return None
    return list(argv)


def run(argv: Sequence[str] | None = None) -> int:
    """Run triage with an optional argument sequence and return its exit code."""

    return _run_review(_copy_arguments(argv))


def cli(argv: Sequence[str] | None = None) -> int:
    """Expose a typed wrapper useful to embedding callers and tests."""

    return run(argv)


def process_arguments() -> list[str]:
    """Return the process arguments without the executable or module name."""

    return sys.argv[1:]


def _exit(code: int) -> NoReturn:
    """Terminate the module process with the triage command's result."""

    raise SystemExit(code)


def _module_main() -> NoReturn:
    """Read process arguments and finish the ``python -m`` invocation."""

    _exit(cli(process_arguments()))


__all__ = ["cli", "process_arguments", "run"]


if __name__ == "__main__":
    _module_main()
