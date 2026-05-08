import logging

from app.jobs.logging import (
    log_scheduler_job_triggered,
    log_scheduler_tick_finished,
    log_worker_run_failed,
    log_worker_tick_finished,
)


def test_log_worker_tick_finished_uses_expected_event(caplog) -> None:
    with caplog.at_level(logging.INFO, logger="app.jobs"):
        log_worker_tick_finished(
            worker_id="worker-1",
            scanned=3,
            executed=2,
            skipped_locked=1,
            failed=0,
        )

    record = caplog.records[-1]
    assert record.event == "worker.tick_finished"
    assert record.component == "worker"
    assert record.worker_id == "worker-1"
    assert record.scanned == 3
    assert record.executed == 2
    assert record.skipped_locked == 1
    assert record.failed == 0


def test_log_scheduler_tick_finished_uses_expected_event(caplog) -> None:
    with caplog.at_level(logging.INFO, logger="app.jobs"):
        log_scheduler_tick_finished(
            scheduler_id="scheduler-1",
            scanned=2,
            triggered=1,
            skipped_locked=0,
            failed=1,
        )

    record = caplog.records[-1]
    assert record.event == "scheduler.tick_finished"
    assert record.component == "scheduler"
    assert record.scheduler_id == "scheduler-1"
    assert record.scanned == 2
    assert record.triggered == 1
    assert record.skipped_locked == 0
    assert record.failed == 1


def test_log_worker_run_failed_adds_exception_context(caplog) -> None:
    with caplog.at_level(logging.ERROR, logger="app.jobs"):
        try:
            raise RuntimeError("remote unavailable")
        except RuntimeError as exc:
            log_worker_run_failed(
                exc,
                worker_id="worker-1",
                run_id=10,
                job_id=3,
                job_type="example.noop",
            )

    record = caplog.records[-1]
    assert record.event == "worker.run_failed"
    assert record.component == "worker"
    assert record.worker_id == "worker-1"
    assert record.run_id == 10
    assert record.job_id == 3
    assert record.job_type == "example.noop"
    assert record.exc_info is not None


def test_log_scheduler_job_triggered_uses_exact_fields(caplog) -> None:
    with caplog.at_level(logging.INFO, logger="app.jobs"):
        log_scheduler_job_triggered(
            scheduler_id="scheduler-1",
            job_id=3,
            job_code="example-noop",
            job_type="example.noop",
        )

    record = caplog.records[-1]
    assert record.event == "scheduler.job_triggered"
    assert record.component == "scheduler"
    assert record.scheduler_id == "scheduler-1"
    assert record.job_id == 3
    assert record.job_code == "example-noop"
    assert record.job_type == "example.noop"
