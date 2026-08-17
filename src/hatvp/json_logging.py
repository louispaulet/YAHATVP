"""Structured JSON logging setup for local runs and Cloud Run jobs."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    """Serialize standard LogRecord fields plus structured event metadata."""

    reserved = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__)

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "severity": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(
            {
                key: value
                for key, value in record.__dict__.items()
                if key not in self.reserved and not key.startswith("_")
            }
        )
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging() -> None:
    """Install one deterministic JSON stream handler on the root logger."""

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)


def structured_event(logger: logging.Logger, event: str, **fields: object) -> None:
    """Emit a named event through the same logging boundary."""

    logger.info(event, extra={"event": event, **fields})


__all__ = ["JsonFormatter", "configure_logging", "structured_event"]
