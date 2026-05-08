from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler
from os import PathLike
from pathlib import Path
from types import TracebackType
from typing import Any, cast

from app.core.config import settings

_STANDARD_RECORD_ATTRS = {
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
    "taskName",
    "thread",
    "threadName",
}

_ExceptionInfo = tuple[type[BaseException], BaseException, TracebackType | None]


class JsonFormatter(logging.Formatter):
    def __init__(self, service_name: str, environment: str) -> None:
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname.lower(),
            "event": getattr(record, "event", "log.message"),
            "service": self.service_name,
            "environment": self.environment,
            "logger": record.name,
            "component": getattr(record, "component", "application"),
            "message": record.getMessage(),
        }
        payload.update(_record_extra(record))

        if record.exc_info:
            exception_info = _resolve_exception_info(record.exc_info)
            if exception_info is not None:
                exc_type, exc_value, traceback = exception_info
                payload["error_type"] = exc_type.__name__
                payload["error_message"] = str(exc_value)
                payload["stacktrace"] = self.formatException(
                    (exc_type, exc_value, traceback)
                )

        return json.dumps(_safe_json(payload), ensure_ascii=False, separators=(",", ":"))


def configure_logging(
    *,
    log_level: str | None = None,
    service_name: str | None = None,
    environment: str | None = None,
    log_output: str | None = None,
    log_file_path: str | PathLike[str] | None = None,
    log_file_max_bytes: int | None = None,
    log_file_backup_count: int | None = None,
) -> None:
    level_name = (log_level or settings.log_level).upper()
    level = getattr(logging, level_name, logging.INFO)
    formatter = JsonFormatter(
        service_name=service_name or settings.service_name,
        environment=environment or settings.environment,
    )
    handlers = _build_handlers(
        log_output=log_output or settings.log_output,
        formatter=formatter,
        log_file_path=log_file_path or settings.log_file_path,
        log_file_max_bytes=log_file_max_bytes or settings.log_file_max_bytes,
        log_file_backup_count=(
            log_file_backup_count
            if log_file_backup_count is not None
            else settings.log_file_backup_count
        ),
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)
    for handler in handlers:
        root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def _build_handlers(
    *,
    log_output: str,
    formatter: JsonFormatter,
    log_file_path: str | PathLike[str],
    log_file_max_bytes: int,
    log_file_backup_count: int,
) -> list[logging.Handler]:
    normalized_output = log_output.lower()
    if normalized_output not in {"stdout", "file", "both"}:
        normalized_output = "stdout"

    handlers: list[logging.Handler] = []
    if normalized_output in {"stdout", "both"}:
        handlers.append(logging.StreamHandler(sys.stdout))

    if normalized_output in {"file", "both"}:
        selected_log_file_path = Path(log_file_path)
        selected_log_file_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                selected_log_file_path,
                maxBytes=log_file_max_bytes,
                backupCount=log_file_backup_count,
                encoding="utf-8",
            )
        )

    for handler in handlers:
        handler.setFormatter(formatter)

    return handlers


def _record_extra(record: logging.LogRecord) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.__dict__.items()
        if key not in _STANDARD_RECORD_ATTRS
        and not key.startswith("_")
        and key not in {"event", "component"}
    }


def _resolve_exception_info(exc_info: object) -> _ExceptionInfo | None:
    if isinstance(exc_info, tuple) and len(exc_info) == 3:
        exc_type, exc_value, traceback = exc_info
    else:
        exc_type, exc_value, traceback = sys.exc_info()

    if (
        isinstance(exc_type, type)
        and issubclass(exc_type, BaseException)
        and isinstance(exc_value, BaseException)
    ):
        return (exc_type, exc_value, cast(TracebackType | None, traceback))
    return None


def _safe_json(value: Any) -> Any:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, dict):
        return {str(key): _safe_json(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set):
        return [_safe_json(item) for item in value]
    return str(value)
