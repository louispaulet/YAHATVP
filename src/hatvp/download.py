"""Reliable source download with exact-byte hashing and bounded retries."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from .download_validation import validate_dataset_prefix
from .hashing import sha256_file

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DownloadedFile:
    name: str
    url: str
    path: Path
    size_bytes: int
    sha256: str
    elapsed_seconds: float


def download_to_path(
    url: str,
    name: str,
    destination: Path,
    *,
    user_agent: str,
    connect_timeout_seconds: float,
    read_timeout_seconds: float,
    retries: int,
) -> DownloadedFile:
    """Download exact response bytes to a temporary file, then publish atomically."""

    timeout = httpx.Timeout(read_timeout_seconds, connect=connect_timeout_seconds)
    last_error: Exception | None = None
    destination.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retries + 1):
        started = time.perf_counter()
        temporary = destination.with_name(f".{destination.name}.part")
        try:
            _download_once(url, temporary, user_agent, timeout)
            validate_dataset_prefix(temporary, name)
            temporary.replace(destination)
            result = DownloadedFile(
                name,
                url,
                destination,
                destination.stat().st_size,
                sha256_file(destination),
                time.perf_counter() - started,
            )
            logger.info(
                "download_complete",
                extra={
                    "event": "download_complete",
                    "file_name": name,
                    "url": url,
                    "size_bytes": result.size_bytes,
                    "sha256": result.sha256,
                    "elapsed_seconds": round(result.elapsed_seconds, 3),
                    "attempt": attempt,
                },
            )
            return result
        except (httpx.HTTPError, OSError, ValueError) as exc:
            last_error = exc
            temporary.unlink(missing_ok=True)
            if attempt < retries:
                logger.warning(
                    "download_retry",
                    extra={
                        "event": "download_retry",
                        "file_name": name,
                        "attempt": attempt,
                        "error": str(exc),
                    },
                )
    raise RuntimeError(
        f"Unable to download {url} after {retries} attempts: {last_error}"
    ) from last_error


def _download_once(url: str, destination: Path, user_agent: str, timeout: httpx.Timeout) -> None:
    with httpx.Client(
        follow_redirects=True, timeout=timeout, headers={"User-Agent": user_agent}
    ) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            with destination.open("wb") as output:
                for chunk in response.iter_bytes():
                    output.write(chunk)


__all__ = ["DownloadedFile", "download_to_path"]
