from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, MutableMapping, Optional

import contextvars

from nlbone.config.settings import get_settings

# Context variable for request/correlation id
_request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "request_id", default=None
)


def set_request_id(request_id: Optional[str]) -> None:
    """
    Set request id in context (e.g., per incoming HTTP request).
    Example:
        from nlbone.config.logging import set_request_id
        set_request_id("abc-123")
    """
    _request_id_var.set(request_id)


class RequestIdFilter(logging.Filter):
    """Injects request_id from contextvars into record."""

    def filter(self, record: logging.LogRecord) -> bool:
        rid = _request_id_var.get()
        # attach as record attribute; formatters can use %(request_id)s
        record.request_id = rid or "-"
        return True


class JsonFormatter(logging.Formatter):
    """Minimal JSON formatter with ISO8601 timestamps."""

    def format(self, record: logging.LogRecord) -> str:
        payload: MutableMapping[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }

        # Add extras (fields set via logger.bind-like approach: logger.info("x", extra={"k": "v"}))
        # Python's logging puts extras into record.__dict__ directly.
        for key, value in record.__dict__.items():
            if key in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            }:
                continue
            # Avoid overriding our top-level keys
            if key in payload:
                continue
            payload[key] = value

        # Attach exception info if present
        if record.exc_info:
            payload["exc_type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def _build_stream_handler(json_enabled: bool, level: int) -> logging.Handler:
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(level)
    handler.addFilter(RequestIdFilter())
    if json_enabled:
        handler.setFormatter(JsonFormatter())
    else:
        # human-friendly text format
        fmt = (
            "%(asctime)s | %(levelname)s | %(name)s | rid=%(request_id)s | %(message)s"
        )
        datefmt = "%Y-%m-%dT%H:%M:%S%z"
        handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    return handler


def setup_logging(
    level: Optional[int] = None,
    json_enabled: Optional[bool] = None,
    silence_uvicorn_access: bool = True,
) -> None:
    """
    Configure root logging once at app start.
    Idempotent: safe to call multiple times.

    Example:
        from nlbone.config.logging import setup_logging
        setup_logging()
    """
    settings = get_settings()
    lvl = level if level is not None else getattr(logging, settings.LOG_LEVEL, logging.INFO)
    json_logs = settings.LOG_JSON if json_enabled is None else json_enabled

    # Clear existing handlers
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    root.setLevel(lvl)
    root.addHandler(_build_stream_handler(json_logs, lvl))

    # Common noisy loggers (optional tweaks)
    for noisy in ("asyncio", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Uvicorn / FastAPI compatibility (if used later)
    # - application logs go through root
    # - format access logs separately or silence them
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.handlers = []
    uvicorn_error.propagate = True  # bubble up to root

    uvicorn_access = logging.getLogger("uvicorn.access")
    if silence_uvicorn_access:
        uvicorn_access.handlers = []
        uvicorn_access.propagate = False
    else:
        uvicorn_access.handlers = []
        uvicorn_access.propagate = True


def get_logger(name: str) -> logging.Logger:
    """
    Helper to get a configured logger.
    Example:
        logger = get_logger(__name__)
        logger.info("hello", extra={"user_id": "42"})
    """
    return logging.getLogger(name)
