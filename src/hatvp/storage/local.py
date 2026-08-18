"""Filesystem implementation of the immutable artifact-store contract."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from ..hashing import sha256_bytes, sha256_file


class LocalArtifactStore:
    """Store artifacts beneath a validated root and optional prefix."""

    def __init__(self, root: Path, prefix: str = "") -> None:
        self.root = root
        self.prefix = prefix.strip("/")

    def _path(self, relative_path: str) -> Path:
        base = (self.root / self.prefix).resolve()
        candidate = (self.root / self.prefix / relative_path).resolve()
        if candidate != base and base not in candidate.parents:
            raise ValueError(f"Invalid artifact path: {relative_path}")
        return candidate

    def exists(self, relative_path: str) -> bool:
        return self._path(relative_path).exists()

    def read_bytes(self, relative_path: str) -> bytes:
        return self._path(relative_path).read_bytes()

    def list_paths(self, relative_prefix: str) -> list[str]:
        """List files below one logical prefix in deterministic order."""

        root = self._path(relative_prefix)
        if not root.exists():
            return []
        base = self._path("")
        return sorted(str(path.relative_to(base)) for path in root.rglob("*") if path.is_file())

    def put_bytes(
        self,
        relative_path: str,
        content: bytes,
        *,
        content_type: str | None = None,
        immutable: bool = False,
    ) -> None:
        destination = self._path(relative_path)
        if immutable and destination.exists():
            if sha256_file(destination) != sha256_bytes(content):
                raise FileExistsError(
                    f"Immutable artifact already exists with different bytes: {relative_path}"
                )
            return
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.tmp")
        temporary.write_bytes(content)
        os.replace(temporary, destination)

    def put_file(
        self,
        relative_path: str,
        source: Path,
        *,
        content_type: str | None = None,
        immutable: bool = False,
    ) -> None:
        destination = self._path(relative_path)
        if immutable and destination.exists():
            if sha256_file(destination) != sha256_file(source):
                raise FileExistsError(
                    f"Immutable artifact already exists with different bytes: {relative_path}"
                )
            return
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.tmp")
        shutil.copyfile(source, temporary)
        os.replace(temporary, destination)

    def put_json(self, relative_path: str, value: object) -> None:
        from . import json_bytes

        self.put_bytes(relative_path, json_bytes(value), content_type="application/json")
