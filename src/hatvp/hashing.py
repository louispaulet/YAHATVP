"""Exact-byte SHA-256 helpers used for provenance and immutable writes."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO

DEFAULT_CHUNK_SIZE = 1024 * 1024


def sha256_stream(source: BinaryIO, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """Hash a binary stream without loading the source into memory."""

    digest = hashlib.sha256()
    while chunk := source.read(chunk_size):
        digest.update(chunk)
    return digest.hexdigest()


def sha256_file(path: Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    with path.open("rb") as source:
        return sha256_stream(source, chunk_size)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def same_bytes(left: bytes, right: bytes) -> bool:
    """Compare byte payloads by digest while retaining exact-byte semantics."""

    return sha256_bytes(left) == sha256_bytes(right) and left == right


def digest_metadata(path: Path) -> dict[str, int | str]:
    """Return size and digest fields suitable for source provenance metadata."""

    return {"size_bytes": path.stat().st_size, "sha256": sha256_file(path)}


__all__ = [
    "DEFAULT_CHUNK_SIZE",
    "digest_metadata",
    "same_bytes",
    "sha256_bytes",
    "sha256_file",
    "sha256_stream",
]
