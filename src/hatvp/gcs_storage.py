"""Google Cloud Storage implementation of the artifact-store contract."""

from __future__ import annotations

from pathlib import Path

from google.api_core.exceptions import PreconditionFailed

from .hashing import sha256_bytes


class GCSArtifactStore:
    """Use ADC-backed GCS objects with generation-guarded immutable writes."""

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
        kwargs = (
            {"content_type": content_type, "if_generation_match": 0}
            if immutable
            else {"content_type": content_type}
        )
        try:
            blob.upload_from_string(content, **kwargs)
        except PreconditionFailed:
            if not immutable or not blob.exists() or blob.download_as_bytes() != content:
                raise

    def put_file(
        self,
        relative_path: str,
        source: Path,
        *,
        content_type: str | None = None,
        immutable: bool = False,
    ) -> None:
        blob = self._blob(relative_path)
        kwargs = (
            {"content_type": content_type, "if_generation_match": 0}
            if immutable
            else {"content_type": content_type}
        )
        try:
            blob.upload_from_filename(str(source), **kwargs)
        except PreconditionFailed:
            if (
                not immutable
                or not blob.exists()
                or sha256_bytes(blob.download_as_bytes()) != sha256_bytes(source.read_bytes())
            ):
                raise

    def put_json(self, relative_path: str, value: object) -> None:
        from .storage import json_bytes

        self.put_bytes(relative_path, json_bytes(value), content_type="application/json")
