from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Protocol

from google.api_core.exceptions import PreconditionFailed

from .hashing import sha256_bytes, sha256_file


class ArtifactStore(Protocol):
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


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


class LocalArtifactStore:
    def __init__(self, root: Path, prefix: str = "") -> None:
        self.root = root
        self.prefix = prefix.strip("/")

    def _path(self, relative_path: str) -> Path:
        candidate = self.root / self.prefix / relative_path
        resolved_root = (self.root / self.prefix).resolve()
        resolved_candidate = candidate.resolve()
        if resolved_root != resolved_candidate and resolved_root not in resolved_candidate.parents:
            raise ValueError(f"Invalid artifact path: {relative_path}")
        return candidate

    def exists(self, relative_path: str) -> bool:
        return self._path(relative_path).exists()

    def read_bytes(self, relative_path: str) -> bytes:
        return self._path(relative_path).read_bytes()

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
        self.put_bytes(relative_path, _json_bytes(value), content_type="application/json")


class GCSArtifactStore:
    def __init__(self, bucket_name: str, prefix: str = "") -> None:
        from google.cloud import storage

        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        self.prefix = prefix.strip("/")

    def _key(self, relative_path: str) -> str:
        return (
            f"{self.prefix}/{relative_path.lstrip('/')}"
            if self.prefix
            else relative_path.lstrip("/")
        )

    def _blob(self, relative_path: str):
        return self.bucket.blob(self._key(relative_path))

    def exists(self, relative_path: str) -> bool:
        return self._blob(relative_path).exists()

    def read_bytes(self, relative_path: str) -> bytes:
        return self._blob(relative_path).download_as_bytes()

    def put_bytes(
        self,
        relative_path: str,
        content: bytes,
        *,
        content_type: str | None = None,
        immutable: bool = False,
    ) -> None:
        blob = self._blob(relative_path)
        kwargs = {"content_type": content_type}
        if immutable:
            kwargs["if_generation_match"] = 0
        try:
            blob.upload_from_string(content, **kwargs)
        except PreconditionFailed:
            if not immutable or not blob.exists() or blob.download_as_bytes() != content:
                raise
            return

    def put_file(
        self,
        relative_path: str,
        source: Path,
        *,
        content_type: str | None = None,
        immutable: bool = False,
    ) -> None:
        blob = self._blob(relative_path)
        kwargs = {"content_type": content_type}
        if immutable:
            kwargs["if_generation_match"] = 0
        try:
            blob.upload_from_filename(str(source), **kwargs)
        except PreconditionFailed:
            if (
                not immutable
                or not blob.exists()
                or blob.download_as_bytes() != source.read_bytes()
            ):
                raise

    def put_json(self, relative_path: str, value: object) -> None:
        self.put_bytes(relative_path, _json_bytes(value), content_type="application/json")
