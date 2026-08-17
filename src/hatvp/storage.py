"""Artifact-store protocol and compatibility exports for local and GCS stores."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from .gcs_storage import GCSArtifactStore
from .local_storage import LocalArtifactStore


class ArtifactStore(Protocol):
    """Minimal storage interface required by all pipeline stages."""

    def exists(self, relative_path: str) -> bool: ...

    def read_bytes(self, relative_path: str) -> bytes: ...

    def put_bytes(
        self,
        relative_path: str,
        content: bytes,
        *,
        content_type: str | None = None,
        immutable: bool = False,
    ) -> None: ...

    def put_file(
        self,
        relative_path: str,
        source: Path,
        *,
        content_type: str | None = None,
        immutable: bool = False,
    ) -> None: ...


def json_bytes(value: object) -> bytes:
    """Serialize metadata consistently across local and cloud stores."""

    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def artifact_uri(prefix: str, relative_path: str) -> str:
    """Join a logical artifact prefix without introducing duplicate slashes."""

    return f"{prefix.rstrip('/')}/{relative_path.lstrip('/')}"


def artifact_path(prefix: str, relative_path: str) -> tuple[str, str]:
    """Return normalized prefix and relative path for adapter diagnostics."""

    return prefix.strip("/"), relative_path.strip("/")


def is_immutable_artifact(relative_path: str) -> bool:
    """Identify raw artifacts whose bytes must not be overwritten."""

    return relative_path.lstrip("/").startswith("raw/")


def store_classes() -> tuple[type, type]:
    """Expose implementations for diagnostics and adapter tests."""

    return LocalArtifactStore, GCSArtifactStore


__all__ = [
    "ArtifactStore",
    "GCSArtifactStore",
    "LocalArtifactStore",
    "artifact_uri",
    "artifact_path",
    "is_immutable_artifact",
    "json_bytes",
    "store_classes",
]
