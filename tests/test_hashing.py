from pathlib import Path

from hatvp.hashing import sha256_bytes, sha256_file


def test_sha256_bytes_and_file_match(tmp_path: Path) -> None:
    path = tmp_path / "payload.bin"
    path.write_bytes(b"hatvp\x00bytes")

    assert sha256_file(path) == sha256_bytes(b"hatvp\x00bytes")
