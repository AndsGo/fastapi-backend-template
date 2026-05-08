import logging

from app.jobs import runner
from app.jobs.run_worker import ConcurrentScheduledRunWorker
from app.jobs.scheduler import DistributedScheduler


def test_build_scheduler_creates_distributed_scheduler() -> None:
    session = object()
    scheduler = runner.build_scheduler(session, scheduler_id="scheduler-test")

    assert isinstance(scheduler, DistributedScheduler)


def test_build_run_worker_creates_concurrent_scheduled_run_worker() -> None:
    session_factory = runner.get_session_local()
    worker = runner.build_run_worker(
        session_factory=session_factory,
        worker_id="worker-test",
        max_workers=2,
    )

    assert isinstance(worker, ConcurrentScheduledRunWorker)


def test_build_job_registry_includes_example_router_handlers() -> None:
    registry = runner.build_job_registry(object())

    assert registry.get("example.noop")


def test_run_loop_logs_scheduler_summary(monkeypatch, caplog) -> None:
    args = runner.parse_args_from_list(
        ["scheduler", "--once", "--scheduler-id", "scheduler-1"]
    )
    monkeypatch.setattr(
        runner,
        "run_scheduler_once",
        lambda *, scheduler_id, limit: {
            "scanned": 1,
            "triggered": 1,
            "skipped_locked": 0,
            "failed": 0,
        },
    )

    with caplog.at_level(logging.INFO, logger="app.jobs"):
        runner.run_loop(args)

    events = [record.event for record in caplog.records]
    assert "scheduler.started" in events
    assert "scheduler.tick_started" in events
    assert "scheduler.tick_finished" in events


def test_run_loop_logs_worker_summary(monkeypatch, caplog) -> None:
    args = runner.parse_args_from_list(
        ["worker", "--once", "--worker-id", "worker-1", "--max-workers", "2"]
    )
    monkeypatch.setattr(
        runner,
        "run_worker_once",
        lambda *, worker_id, limit, max_workers, lock_ttl_seconds: {
            "scanned": 1,
            "executed": 1,
            "skipped_locked": 0,
            "failed": 0,
        },
    )

    with caplog.at_level(logging.INFO, logger="app.jobs"):
        runner.run_loop(args)

    events = [record.event for record in caplog.records]
    assert "worker.started" in events
    assert "worker.tick_started" in events
    assert "worker.tick_finished" in events
