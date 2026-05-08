import json
import logging
import sys
from pathlib import Path

from app.core.logging import JsonFormatter, configure_logging, get_logger


def test_json_formatter_emits_required_fields() -> None:
    formatter = JsonFormatter("fastapi-backend-template", "test")
    record = logging.LogRecord(
        name="app.jobs.runner",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Worker tick finished",
        args=(),
        exc_info=None,
    )
    record.event = "worker.tick_finished"
    record.component = "worker"
    record.worker_id = "worker-1"
    record.executed = 2

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "info"
    assert payload["event"] == "worker.tick_finished"
    assert payload["service"] == "fastapi-backend-template"
    assert payload["environment"] == "test"
    assert payload["logger"] == "app.jobs.runner"
    assert payload["component"] == "worker"
    assert payload["message"] == "Worker tick finished"
    assert payload["worker_id"] == "worker-1"
    assert payload["executed"] == 2
    assert "timestamp" in payload
    assert "taskName" not in payload


def test_json_formatter_includes_exception_fields() -> None:
    formatter = JsonFormatter(service_name="fastapi-backend-template", environment="test")

    try:
        raise RuntimeError("remote unavailable")
    except RuntimeError:
        record = logging.getLogger("app.jobs.run_worker").makeRecord(
            name="app.jobs.run_worker",
            level=logging.ERROR,
            fn=__file__,
            lno=30,
            msg="Scheduled run failed",
            args=(),
            exc_info=sys.exc_info(),
            func=None,
            extra={
                "event": "worker.run_failed",
                "component": "worker",
            },
        )

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "error"
    assert payload["error_type"] == "RuntimeError"
    assert payload["error_message"] == "remote unavailable"
    assert "RuntimeError: remote unavailable" in payload["stacktrace"]


def test_json_formatter_stringifies_non_json_extra_values() -> None:
    formatter = JsonFormatter(service_name="fastapi-backend-template", environment="test")
    non_json_payload = object()
    record = logging.getLogger("app.jobs.runner").makeRecord(
        name="app.jobs.runner",
        level=logging.INFO,
        fn=__file__,
        lno=40,
        msg="Worker tick finished",
        args=(),
        exc_info=None,
        func=None,
        extra={
            "event": "worker.tick_finished",
            "component": "worker",
            "payload": non_json_payload,
        },
    )

    payload = json.loads(formatter.format(record))

    assert payload["payload"] == str(non_json_payload)


def test_configure_logging_writes_json_to_stdout(capsys) -> None:
    configure_logging(
        log_level="INFO",
        service_name="fastapi-backend-template",
        environment="test",
    )
    logger = get_logger("app.jobs.runner")

    logger.info(
        "Worker tick finished",
        extra={"event": "worker.tick_finished", "component": "worker"},
    )

    payload = json.loads(capsys.readouterr().out)

    assert payload["event"] == "worker.tick_finished"
    assert payload["service"] == "fastapi-backend-template"
    assert payload["environment"] == "test"


def test_configure_logging_writes_json_to_file(tmp_path: Path, capsys) -> None:
    log_file_path = tmp_path / "nested" / "app.log"
    configure_logging(
        log_level="INFO",
        service_name="fastapi-backend-template",
        environment="test",
        log_output="file",
        log_file_path=log_file_path,
    )
    logger = get_logger("app.jobs.runner")

    logger.info(
        "Worker tick finished",
        extra={"event": "worker.tick_finished", "component": "worker"},
    )

    assert capsys.readouterr().out == ""
    payload = json.loads(log_file_path.read_text(encoding="utf-8"))

    assert payload["event"] == "worker.tick_finished"
    assert payload["service"] == "fastapi-backend-template"
    assert payload["environment"] == "test"


def test_configure_logging_writes_json_to_stdout_and_file(
    tmp_path: Path,
    capsys,
) -> None:
    log_file_path = tmp_path / "app.log"
    configure_logging(
        log_level="INFO",
        service_name="fastapi-backend-template",
        environment="test",
        log_output="both",
        log_file_path=log_file_path,
    )
    logger = get_logger("app.jobs.runner")

    logger.info(
        "Worker tick finished",
        extra={"event": "worker.tick_finished", "component": "worker"},
    )

    stdout_payload = json.loads(capsys.readouterr().out)
    file_payload = json.loads(log_file_path.read_text(encoding="utf-8"))

    assert stdout_payload["event"] == "worker.tick_finished"
    assert file_payload["event"] == "worker.tick_finished"

