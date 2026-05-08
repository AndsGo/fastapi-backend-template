from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import app.jobs.run_worker as run_worker_module
from app.domains.enums import ScheduledJobRunStatus
from app.jobs.registry import JobContext, JobRegistry, JobResult
from app.jobs.run_worker import ConcurrentScheduledRunWorker


@dataclass
class FakeJob:
    id: int
    job_type: str
    payload: dict[str, Any] | None = None


@dataclass
class FakeRun:
    id: int
    job_id: int
    job: FakeJob
    status: ScheduledJobRunStatus = ScheduledJobRunStatus.pending
    triggered_by: str = "scheduler"
    worker_id: str | None = None
    result: dict[str, Any] | None = None
    error_message: str | None = None


class FakeSession:
    def __init__(self) -> None:
        self.closed = False
        self.commit_count = 0

    def commit(self) -> None:
        self.commit_count += 1

    def close(self) -> None:
        self.closed = True


class FakeRunRepository:
    def __init__(self, runs: dict[int, FakeRun], session: FakeSession) -> None:
        self.runs = runs
        self.db = session

    def list_runnable_runs(self, now: datetime, limit: int = 100) -> list[FakeRun]:
        return [
            run
            for run in sorted(self.runs.values(), key=lambda candidate: candidate.id)
            if run.status == ScheduledJobRunStatus.pending
        ][:limit]

    def claim_run_running(
        self,
        run_id: int,
        *,
        worker_id: str,
        locked_until: datetime,
        now: datetime,
    ) -> FakeRun | None:
        run = self.runs.get(run_id)
        if run is None or run.status != ScheduledJobRunStatus.pending:
            return None
        run.status = ScheduledJobRunStatus.running
        run.worker_id = worker_id
        return run

    def apply_success_state(self, run: FakeRun, *, result: dict[str, Any]) -> FakeRun:
        run.status = ScheduledJobRunStatus.succeeded
        run.result = result
        return run

    def apply_failure_state(self, run: FakeRun, *, error_message: str) -> FakeRun:
        run.status = ScheduledJobRunStatus.failed
        run.error_message = error_message
        return run


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.lock = threading.Lock()

    def set(self, key: str, value: str, *, nx: bool, ex: int) -> bool:
        with self.lock:
            if nx and key in self.values:
                return False
            self.values[key] = value
            return True

    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> int:
        key, owner_token = keys_and_args[:2]
        with self.lock:
            if self.values.get(key) != owner_token:
                return 0
            del self.values[key]
            return 1


def test_run_worker_consumes_pending_runs_and_executes_registered_handler() -> None:
    runs = {
        1: FakeRun(
            id=1,
            job_id=10,
            job=FakeJob(id=10, job_type="example.noop", payload={"limit": 5}),
        )
    }
    sessions: list[FakeSession] = []

    def session_factory() -> FakeSession:
        session = FakeSession()
        sessions.append(session)
        return session

    def repository_factory(session: FakeSession) -> FakeRunRepository:
        return FakeRunRepository(runs, session)

    registry = JobRegistry()

    def handler(context: JobContext) -> JobResult:
        assert context.run_id == 1
        assert context.job_id == 10
        assert context.job_type == "example.noop"
        assert context.payload == {"limit": 5}
        assert context.worker_id == "run-worker-1"
        return JobResult(processed_count=5, succeeded_count=5)

    registry.register("example.noop", handler)
    worker = ConcurrentScheduledRunWorker(
        session_factory=session_factory,
        run_repository_factory=repository_factory,
        registry=registry,
        redis_client=FakeRedis(),
        worker_id="run-worker-1",
        max_workers=2,
    )

    result = worker.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert result == {"scanned": 1, "executed": 1, "skipped_locked": 0, "failed": 0}
    assert runs[1].status == ScheduledJobRunStatus.succeeded
    assert runs[1].result == {
        "status": "succeeded",
        "processed_count": 5,
        "succeeded_count": 5,
        "failed_count": 0,
        "details": {},
    }
    assert len(sessions) == 2
    assert all(session.closed for session in sessions)


def test_run_worker_marks_run_failed_when_handler_raises() -> None:
    runs = {
        1: FakeRun(
            id=1,
            job_id=10,
            job=FakeJob(id=10, job_type="example.noop", payload={}),
        )
    }

    def session_factory() -> FakeSession:
        return FakeSession()

    def repository_factory(session: FakeSession) -> FakeRunRepository:
        return FakeRunRepository(runs, session)

    registry = JobRegistry()

    def handler(context: JobContext) -> JobResult:
        raise RuntimeError("remote unavailable")

    registry.register("example.noop", handler)
    worker = ConcurrentScheduledRunWorker(
        session_factory=session_factory,
        run_repository_factory=repository_factory,
        registry=registry,
        redis_client=FakeRedis(),
        worker_id="run-worker-1",
        max_workers=2,
    )

    result = worker.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert result == {"scanned": 1, "executed": 0, "skipped_locked": 0, "failed": 1}
    assert runs[1].status == ScheduledJobRunStatus.failed
    assert runs[1].error_message == "remote unavailable"


def test_worker_logs_claim_and_success(caplog) -> None:
    runs = {
        1: FakeRun(
            id=1,
            job_id=10,
            job=FakeJob(id=10, job_type="example.noop", payload={"limit": 5}),
        )
    }
    registry = JobRegistry()

    def session_factory() -> FakeSession:
        return FakeSession()

    def repository_factory(session: FakeSession) -> FakeRunRepository:
        return FakeRunRepository(runs, session)

    def handler(context: JobContext) -> JobResult:
        return JobResult(processed_count=5, succeeded_count=5)

    registry.register("example.noop", handler)
    worker = ConcurrentScheduledRunWorker(
        session_factory=session_factory,
        run_repository_factory=repository_factory,
        registry=registry,
        redis_client=FakeRedis(),
        worker_id="worker-1",
        max_workers=1,
    )

    with caplog.at_level(logging.INFO, logger="app.jobs"):
        worker.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    claimed = next(record for record in caplog.records if record.event == "worker.run_claimed")
    assert claimed.component == "worker"
    assert claimed.worker_id == "worker-1"
    assert claimed.run_id == 1
    assert claimed.job_id == 10
    assert claimed.job_type == "example.noop"

    executed = next(
        record for record in caplog.records if record.event == "worker.run_executed"
    )
    assert executed.component == "worker"
    assert executed.worker_id == "worker-1"
    assert executed.run_id == 1
    assert executed.job_id == 10
    assert executed.job_type == "example.noop"
    assert executed.result == {
        "status": "succeeded",
        "processed_count": 5,
        "succeeded_count": 5,
        "failed_count": 0,
        "details": {},
    }


def test_worker_logs_failure_with_exception(caplog) -> None:
    runs = {
        1: FakeRun(
            id=1,
            job_id=10,
            job=FakeJob(id=10, job_type="example.noop", payload={}),
        )
    }
    registry = JobRegistry()

    def session_factory() -> FakeSession:
        return FakeSession()

    def repository_factory(session: FakeSession) -> FakeRunRepository:
        return FakeRunRepository(runs, session)

    def handler(context: JobContext) -> JobResult:
        raise RuntimeError("remote unavailable")

    registry.register("example.noop", handler)
    worker = ConcurrentScheduledRunWorker(
        session_factory=session_factory,
        run_repository_factory=repository_factory,
        registry=registry,
        redis_client=FakeRedis(),
        worker_id="worker-1",
        max_workers=1,
    )

    with caplog.at_level(logging.ERROR, logger="app.jobs"):
        worker.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    record = next(record for record in caplog.records if record.event == "worker.run_failed")
    assert record.component == "worker"
    assert record.worker_id == "worker-1"
    assert record.run_id == 1
    assert record.job_id == 10
    assert record.job_type == "example.noop"
    assert record.exc_info is not None


def test_worker_executes_handler_when_claim_logging_raises(monkeypatch) -> None:
    runs = {
        1: FakeRun(
            id=1,
            job_id=10,
            job=FakeJob(id=10, job_type="example.noop", payload={}),
        )
    }
    registry = JobRegistry()
    handler_calls: list[int] = []

    def session_factory() -> FakeSession:
        return FakeSession()

    def repository_factory(session: FakeSession) -> FakeRunRepository:
        return FakeRunRepository(runs, session)

    def handler(context: JobContext) -> JobResult:
        handler_calls.append(context.run_id)
        return JobResult(processed_count=1, succeeded_count=1)

    def raise_logging_error(**kwargs: object) -> None:
        raise RuntimeError("logging unavailable")

    monkeypatch.setattr(
        run_worker_module,
        "log_worker_run_claimed",
        raise_logging_error,
    )

    registry.register("example.noop", handler)
    worker = ConcurrentScheduledRunWorker(
        session_factory=session_factory,
        run_repository_factory=repository_factory,
        registry=registry,
        redis_client=FakeRedis(),
        worker_id="worker-1",
        max_workers=1,
    )

    result = worker.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert result == {"scanned": 1, "executed": 1, "skipped_locked": 0, "failed": 0}
    assert handler_calls == [1]
    assert runs[1].status == ScheduledJobRunStatus.succeeded


def test_worker_keeps_success_state_when_success_logging_raises(monkeypatch) -> None:
    runs = {
        1: FakeRun(
            id=1,
            job_id=10,
            job=FakeJob(id=10, job_type="example.noop", payload={}),
        )
    }
    registry = JobRegistry()

    def session_factory() -> FakeSession:
        return FakeSession()

    def repository_factory(session: FakeSession) -> FakeRunRepository:
        return FakeRunRepository(runs, session)

    def handler(context: JobContext) -> JobResult:
        return JobResult(processed_count=1, succeeded_count=1)

    def raise_logging_error(**kwargs: object) -> None:
        raise RuntimeError("logging unavailable")

    monkeypatch.setattr(
        run_worker_module,
        "log_worker_run_executed",
        raise_logging_error,
    )

    registry.register("example.noop", handler)
    worker = ConcurrentScheduledRunWorker(
        session_factory=session_factory,
        run_repository_factory=repository_factory,
        registry=registry,
        redis_client=FakeRedis(),
        worker_id="worker-1",
        max_workers=1,
    )

    result = worker.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert result == {"scanned": 1, "executed": 1, "skipped_locked": 0, "failed": 0}
    assert runs[1].status == ScheduledJobRunStatus.succeeded
    assert runs[1].result == {
        "status": "succeeded",
        "processed_count": 1,
        "succeeded_count": 1,
        "failed_count": 0,
        "details": {},
    }
    assert runs[1].error_message is None

