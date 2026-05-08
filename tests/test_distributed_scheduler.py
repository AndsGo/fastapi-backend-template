from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.domains.enums import ScheduledJobRunStatus, ScheduledJobStatus
from app.jobs.scheduler import DistributedScheduler


@dataclass
class FakeJob:
    id: int
    code: str
    job_type: str
    payload: dict[str, Any] | None
    cron_expression: str = "* * * * *"
    timezone: str = "UTC"
    lock_ttl_seconds: int = 60
    max_runtime_seconds: int = 900
    status: ScheduledJobStatus = ScheduledJobStatus.enabled
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None


@dataclass
class FakeRun:
    id: int
    job_id: int
    status: ScheduledJobRunStatus
    triggered_by: str
    trigger_info: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    error_message: str | None = None
    worker_id: str | None = None


class FakeDb:
    def __init__(self) -> None:
        self.commit_count = 0
        self.rollback_count = 0
        self.needs_rollback = False

    def commit(self) -> None:
        self.commit_count += 1

    def rollback(self) -> None:
        self.rollback_count += 1
        self.needs_rollback = False


class FakeJobRepository:
    def __init__(
        self,
        jobs: list[FakeJob],
        db: FakeDb | None = None,
        job_by_id: dict[int, FakeJob | None] | None = None,
    ) -> None:
        self.jobs = jobs
        self.db = db
        self.job_by_id = job_by_id or {}
        self.schedule_updates = 0

    def list_due_jobs(self, now: datetime, limit: int = 100) -> list[FakeJob]:
        return [
            job for job in self.jobs if job.next_run_at is None or job.next_run_at <= now
        ][:limit]

    def get(self, job_id: int) -> FakeJob | None:
        if job_id in self.job_by_id:
            return self.job_by_id[job_id]
        return next((job for job in self.jobs if job.id == job_id), None)

    def apply_schedule_state(
        self,
        job: FakeJob,
        *,
        last_run_at: datetime,
        next_run_at: datetime | None,
    ) -> FakeJob:
        self.schedule_updates += 1
        job.last_run_at = last_run_at
        job.next_run_at = next_run_at
        return job


class FakeRunRepository:
    def __init__(self, db: FakeDb | None = None) -> None:
        self.db = db
        self.runs: list[FakeRun] = []

    def create(self, payload: dict[str, Any]) -> FakeRun:
        run = FakeRun(
            id=len(self.runs) + 1,
            job_id=payload["job_id"],
            status=payload["status"],
            triggered_by=payload["triggered_by"],
            trigger_info=payload.get("trigger_info"),
        )
        self.runs.append(run)
        return run

    def apply_running_state(self, run: FakeRun, *, worker_id: str) -> FakeRun:
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


class FakeRunRepositoryWithFailedTransaction(FakeRunRepository):
    def create(self, payload: dict[str, Any]) -> FakeRun:
        if self.db is None:
            raise RuntimeError("missing fake db")
        if self.db.needs_rollback:
            raise RuntimeError("transaction requires rollback")
        if payload["job_id"] == 1:
            self.db.needs_rollback = True
            raise RuntimeError("insert failed")
        return super().create(payload)


class FakeRedis:
    def __init__(self, acquire: bool = True) -> None:
        self.acquire = acquire
        self.values: dict[str, str] = {}
        self.set_values: list[str] = []
        self.set_expires: list[int | None] = []

    def set(self, name: str, value: str, nx: bool = False, ex: int | None = None) -> bool:
        if not self.acquire:
            return False
        if nx and name in self.values:
            return False
        self.values[name] = value
        self.set_values.append(value)
        self.set_expires.append(ex)
        return True

    def get(self, name: str) -> str | None:
        return self.values.get(name)

    def expire(self, name: str, time: int) -> bool:
        return name in self.values

    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> int:
        key, owner_token = keys_and_args[:2]
        if self.values.get(key) == owner_token:
            del self.values[key]
            return 1
        return 0


def test_scheduler_skips_job_when_lock_not_acquired() -> None:
    job_repository = FakeJobRepository(
        [FakeJob(id=1, code="example-noop", job_type="example.noop", payload={})]
    )
    run_repository = FakeRunRepository()
    scheduler = DistributedScheduler(
        job_repository=job_repository,
        run_repository=run_repository,
        redis_client=FakeRedis(acquire=False),
        scheduler_id="scheduler-1",
    )

    result = scheduler.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert result == {"scanned": 1, "triggered": 0, "skipped_locked": 1, "failed": 0}
    assert run_repository.runs == []


def test_scheduler_creates_pending_run_without_executing_handler() -> None:
    job_repository = FakeJobRepository(
        [FakeJob(id=1, code="example-noop", job_type="example.noop", payload=None)]
    )
    run_repository = FakeRunRepository()
    scheduler = DistributedScheduler(
        job_repository=job_repository,
        run_repository=run_repository,
        redis_client=FakeRedis(),
        scheduler_id="scheduler-1",
    )
    now = datetime(2026, 5, 7, 10, 0, tzinfo=UTC)

    result = scheduler.run_once(now=now)

    assert result == {"scanned": 1, "triggered": 1, "skipped_locked": 0, "failed": 0}
    assert run_repository.runs[0].status == ScheduledJobRunStatus.pending
    assert run_repository.runs[0].triggered_by == "scheduler-1"
    assert run_repository.runs[0].worker_id is None
    assert run_repository.runs[0].result is None
    assert run_repository.runs[0].trigger_info == {
        "source": "scheduler",
        "scheduler_id": "scheduler-1",
        "scheduled_job_id": 1,
        "scheduled_job_code": "example-noop",
        "scheduled_at": now.isoformat(),
    }
    assert job_repository.schedule_updates == 1
    assert job_repository.jobs[0].last_run_at == now
    assert job_repository.jobs[0].next_run_at == datetime(2026, 5, 7, 10, 1, tzinfo=UTC)


def test_scheduler_logs_triggered_job(caplog) -> None:
    job_repository = FakeJobRepository(
        [FakeJob(id=1, code="example-noop", job_type="example.noop", payload={})]
    )
    run_repository = FakeRunRepository()
    scheduler = DistributedScheduler(
        job_repository=job_repository,
        run_repository=run_repository,
        redis_client=FakeRedis(),
        scheduler_id="scheduler-1",
    )

    with caplog.at_level(logging.INFO, logger="app.jobs"):
        scheduler.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    record = next(
        record for record in caplog.records if record.event == "scheduler.job_triggered"
    )
    assert record.component == "scheduler"
    assert record.scheduler_id == "scheduler-1"
    assert record.job_id == 1
    assert record.job_code == "example-noop"
    assert record.job_type == "example.noop"


def test_scheduler_persists_next_run_at_after_success_and_job_is_not_due_before_then() -> None:
    job_repository = FakeJobRepository(
        [
            FakeJob(
                id=1,
                code="example-noop",
                job_type="example.noop",
                payload={},
                cron_expression="*/10 * * * *",
                next_run_at=datetime(2026, 5, 7, 10, 0, tzinfo=UTC),
            )
        ]
    )
    run_repository = FakeRunRepository()
    scheduler = DistributedScheduler(
        job_repository=job_repository,
        run_repository=run_repository,
        redis_client=FakeRedis(),
        scheduler_id="scheduler-1",
    )
    now = datetime(2026, 5, 7, 10, 0, tzinfo=UTC)

    result = scheduler.run_once(now=now)

    assert result == {"scanned": 1, "triggered": 1, "skipped_locked": 0, "failed": 0}
    assert job_repository.jobs[0].next_run_at == datetime(2026, 5, 7, 10, 10, tzinfo=UTC)
    assert job_repository.list_due_jobs(datetime(2026, 5, 7, 10, 9, tzinfo=UTC)) == []
    assert job_repository.list_due_jobs(datetime(2026, 5, 7, 10, 10, tzinfo=UTC)) == [
        job_repository.jobs[0]
    ]


def test_scheduler_can_compare_naive_database_next_run_at_with_aware_now() -> None:
    scanned_job = FakeJob(
        id=1,
        code="example-noop",
        job_type="example.noop",
        payload={},
        cron_expression="*/10 * * * *",
        next_run_at=datetime(2026, 5, 7, 10, 0, tzinfo=UTC),
    )
    reloaded_job = FakeJob(
        id=1,
        code="example-noop",
        job_type="example.noop",
        payload={},
        cron_expression="*/10 * * * *",
        next_run_at=datetime(2026, 5, 7, 10, 0),
    )
    job_repository = FakeJobRepository(
        [scanned_job],
        job_by_id={1: reloaded_job},
    )
    scheduler = DistributedScheduler(
        job_repository=job_repository,
        run_repository=FakeRunRepository(),
        redis_client=FakeRedis(),
        scheduler_id="scheduler-1",
    )

    result = scheduler.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert result == {"scanned": 1, "triggered": 1, "skipped_locked": 0, "failed": 0}


def test_scheduler_skips_stale_job_after_lock_when_reloaded_job_is_disabled() -> None:
    scanned_job = FakeJob(
        id=1,
        code="example-noop",
        job_type="example.noop",
        payload={},
        status=ScheduledJobStatus.enabled,
    )
    reloaded_job = FakeJob(
        id=1,
        code="example-noop",
        job_type="example.noop",
        payload={},
        status=ScheduledJobStatus.disabled,
    )
    job_repository = FakeJobRepository([scanned_job], job_by_id={1: reloaded_job})
    run_repository = FakeRunRepository()
    scheduler = DistributedScheduler(
        job_repository=job_repository,
        run_repository=run_repository,
        redis_client=FakeRedis(),
        scheduler_id="scheduler-1",
    )

    result = scheduler.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert result == {"scanned": 1, "triggered": 0, "skipped_locked": 1, "failed": 0}
    assert run_repository.runs == []
    assert job_repository.schedule_updates == 0


def test_scheduler_commits_after_success_state_changes() -> None:
    db = FakeDb()
    job_repository = FakeJobRepository(
        [FakeJob(id=1, code="example-noop", job_type="example.noop", payload={})],
        db=db,
    )
    run_repository = FakeRunRepository()
    scheduler = DistributedScheduler(
        job_repository=job_repository,
        run_repository=run_repository,
        redis_client=FakeRedis(),
        scheduler_id="scheduler-1",
    )

    scheduler.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert db.commit_count >= 1


def test_scheduler_uses_unique_lock_owner_token_per_job_acquisition() -> None:
    job_repository = FakeJobRepository(
        [FakeJob(id=1, code="example-noop", job_type="example.noop", payload={})]
    )
    run_repository = FakeRunRepository()
    redis = FakeRedis()
    scheduler = DistributedScheduler(
        job_repository=job_repository,
        run_repository=run_repository,
        redis_client=redis,
        scheduler_id="scheduler-1",
    )

    scheduler.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert redis.set_values[0].startswith("scheduler-1:1:")
    assert redis.set_values[0] != "scheduler-1"


def test_scheduler_uses_max_runtime_for_lock_ttl_when_greater_than_lock_ttl() -> None:
    job_repository = FakeJobRepository(
        [
            FakeJob(
                id=1,
                code="example-noop",
                job_type="example.noop",
                payload={},
                lock_ttl_seconds=60,
                max_runtime_seconds=900,
            )
        ]
    )
    run_repository = FakeRunRepository()
    redis = FakeRedis()
    scheduler = DistributedScheduler(
        job_repository=job_repository,
        run_repository=run_repository,
        redis_client=redis,
        scheduler_id="scheduler-1",
    )

    scheduler.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert redis.set_expires[0] == 900


def test_scheduler_logs_failure_when_next_run_cannot_be_computed_before_creating_run(
    caplog,
) -> None:
    job_repository = FakeJobRepository(
        [
            FakeJob(
                id=1,
                code="example-noop",
                job_type="example.noop",
                payload={},
                cron_expression="invalid cron",
            )
        ]
    )
    run_repository = FakeRunRepository()
    scheduler = DistributedScheduler(
        job_repository=job_repository,
        run_repository=run_repository,
        redis_client=FakeRedis(),
        scheduler_id="scheduler-1",
    )

    with caplog.at_level(logging.ERROR, logger="app.jobs"):
        result = scheduler.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert result == {"scanned": 1, "triggered": 0, "skipped_locked": 0, "failed": 1}
    assert run_repository.runs == []
    assert job_repository.schedule_updates == 0
    record = next(
        record for record in caplog.records if record.event == "scheduler.job_failed"
    )
    assert record.component == "scheduler"
    assert record.scheduler_id == "scheduler-1"
    assert record.job_id == 1
    assert record.job_code == "example-noop"
    assert record.job_type == "example.noop"
    assert record.exc_info is not None


def test_scheduler_rolls_back_failed_trigger_state_before_next_job() -> None:
    db = FakeDb()
    job_repository = FakeJobRepository(
        [
            FakeJob(id=1, code="example-noop-1", job_type="example.noop", payload={}),
            FakeJob(id=2, code="example-noop-2", job_type="example.noop", payload={}),
        ],
        db=db,
    )
    run_repository = FakeRunRepositoryWithFailedTransaction(db=db)
    scheduler = DistributedScheduler(
        job_repository=job_repository,
        run_repository=run_repository,
        redis_client=FakeRedis(),
        scheduler_id="scheduler-1",
    )

    result = scheduler.run_once(now=datetime(2026, 5, 7, 10, 0, tzinfo=UTC))

    assert result == {"scanned": 2, "triggered": 1, "skipped_locked": 0, "failed": 1}
    assert db.rollback_count == 1
    assert [run.job_id for run in run_repository.runs] == [2]

