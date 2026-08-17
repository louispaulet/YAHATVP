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


def file_matches_digest(path: Path, expected: str) -> bool:
    """Check a file against a recorded provenance digest."""

    return sha256_file(path) == expected


def digest_pair(left: Path, right: Path) -> bool:
    """Compare two files by digest and size without retaining their contents."""

    return left.stat().st_size == right.stat().st_size and sha256_file(left) == sha256_file(right)


def digest_paths(paths: list[Path]) -> dict[str, str]:
    """Return stable path-to-digest metadata for a batch of source files."""

    return {str(path): sha256_file(path) for path in paths}


def digest_size(path: Path) -> tuple[int, str]:
    """Return the byte length and digest used in source metadata."""

    return path.stat().st_size, sha256_file(path)


__all__ = [
    "DEFAULT_CHUNK_SIZE",
    "digest_metadata",
    "digest_pair",
    "file_matches_digest",
    "same_bytes",
    "sha256_bytes",
    "sha256_file",
    "sha256_stream",
]
