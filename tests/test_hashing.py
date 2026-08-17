"""Unit tests for exact-byte provenance hashing and streaming boundaries."""

import io
from pathlib import Path

from hatvp.hashing import (
    DEFAULT_CHUNK_SIZE,
    digest_metadata,
    digest_pair,
    digest_paths,
    digest_size,
    file_matches_digest,
    same_bytes,
    sha256_bytes,
    sha256_file,
    sha256_stream,
)


def test_sha256_bytes_and_file_match(tmp_path: Path) -> None:
    path = tmp_path / "payload.bin"
    path.write_bytes(b"hatvp\x00bytes")

    assert sha256_file(path) == sha256_bytes(b"hatvp\x00bytes")


def test_digest_metadata_and_file_match_expose_provenance(tmp_path: Path) -> None:
    path = tmp_path / "source.xml"
    path.write_bytes(b"<source />")

    metadata = digest_metadata(path)

    assert metadata["size_bytes"] == path.stat().st_size
    assert metadata["sha256"] == sha256_file(path)
    assert file_matches_digest(path, str(metadata["sha256"]))


def test_digest_pair_and_batch_digests_are_stable(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.write_bytes(b"same")
    second.write_bytes(b"same")

    assert digest_pair(first, second)
    assert digest_paths([first, second]) == {
        str(first): sha256_file(first),
        str(second): sha256_file(second),
    }


def test_same_bytes_requires_equal_payload_not_only_equal_hash() -> None:
    assert same_bytes(b"same", b"same")
    assert not same_bytes(b"left", b"right")


def test_stream_hashing_supports_small_chunks_without_reading_all_bytes() -> None:
    payload = b"hatvp-source" * 20

    assert sha256_stream(io.BytesIO(payload), chunk_size=3) == sha256_bytes(payload)
    assert DEFAULT_CHUNK_SIZE > 0


def test_digest_size_matches_digest_metadata(tmp_path: Path) -> None:
    path = tmp_path / "payload"
    path.write_bytes(b"12345")

    size, digest = digest_size(path)

    assert size == digest_metadata(path)["size_bytes"] == 5
    assert digest == digest_metadata(path)["sha256"]


def test_digest_pair_detects_changed_bytes(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.write_bytes(b"same")
    second.write_bytes(b"different")

    assert not digest_pair(first, second)
