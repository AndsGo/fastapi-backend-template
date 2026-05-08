from datetime import UTC, datetime

import app.repositories.scheduled_job_repository as scheduled_job_repository
from app.domains.enums import ScheduledJobRunStatus
from app.models.scheduled_job import ScheduledJob
from app.models.scheduled_job_run import ScheduledJobRun
from app.repositories.scheduled_job_repository import (
    ScheduledJobRepository,
    ScheduledJobRunRepository,
)


def test_due_jobs_statement_filters_enabled_due_jobs() -> None:
    now = datetime(2026, 5, 7, 12, 0, tzinfo=UTC)

    statement = ScheduledJobRepository.due_jobs_statement(now, limit=50)
    compiled = str(statement)

    assert "scheduled_jobs.status" in compiled
    assert "scheduled_jobs.next_run_at" in compiled
    assert "LIMIT" in compiled


def test_refresh_for_execution_uses_populate_existing() -> None:
    statement = ScheduledJobRepository.refresh_for_execution_statement(1)
    assert statement.get_execution_options()["populate_existing"] is True


def test_mark_run_running_sets_worker_and_started_at() -> None:
    run = ScheduledJobRun(job_id=1, status=ScheduledJobRunStatus.pending)
    run.id = 10
    repository = ScheduledJobRunRepository.__new__(ScheduledJobRunRepository)

    result = repository.apply_running_state(run, worker_id="scheduler-1")

    assert result is run
    assert run.status == ScheduledJobRunStatus.running
    assert run.worker_id == "scheduler-1"
    assert run.started_at is not None
    assert run.heartbeat_at == run.started_at


def test_runnable_runs_statement_filters_pending_runs() -> None:
    now = datetime(2026, 5, 7, 12, 0, tzinfo=UTC)

    statement = ScheduledJobRunRepository.runnable_runs_statement(now, limit=25)
    compiled = str(statement)

    assert "scheduled_job_runs.status" in compiled
    assert "scheduled_job_runs.locked_until" in compiled
    assert "LIMIT" in compiled


def test_claim_run_running_statement_filters_pending_run() -> None:
    now = datetime(2026, 5, 7, 12, 0, tzinfo=UTC)
    locked_until = datetime(2026, 5, 7, 12, 5, tzinfo=UTC)

    statement = ScheduledJobRunRepository.claim_run_running_statement(
        1,
        worker_id="worker-1",
        locked_until=locked_until,
        now=now,
    )
    compiled = str(statement)

    assert "scheduled_job_runs.id" in compiled
    assert "scheduled_job_runs.status" in compiled
    assert "RETURNING scheduled_job_runs.id" in compiled


def test_mark_run_succeeded_sets_result_and_duration_with_naive_started_at() -> None:
    run = ScheduledJobRun(job_id=1, status=ScheduledJobRunStatus.running)
    run.started_at = datetime(2026, 5, 1, 12, 0)
    repository = ScheduledJobRunRepository.__new__(ScheduledJobRunRepository)

    result = repository.apply_success_state(run, result={"processed": 1})

    assert result is run
    assert run.status == ScheduledJobRunStatus.succeeded
    assert run.result == {"processed": 1}
    assert run.finished_at is not None
    assert run.finished_at.tzinfo is None
    assert run.duration_ms is not None
    assert run.duration_ms >= 0


def test_mark_run_succeeded_treats_naive_started_at_as_utc_naive(monkeypatch) -> None:
    seen_tzinfos = []

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            seen_tzinfos.append(tz)
            return cls(2026, 5, 7, 12, 0, 5, tzinfo=tz)

    monkeypatch.setattr(scheduled_job_repository, "datetime", FixedDateTime)
    run = ScheduledJobRun(job_id=1, status=ScheduledJobRunStatus.running)
    run.started_at = datetime(2026, 5, 7, 12, 0)
    repository = ScheduledJobRunRepository.__new__(ScheduledJobRunRepository)

    repository.apply_success_state(run, result={"processed": 1})

    assert seen_tzinfos == [UTC]
    assert run.finished_at == datetime(2026, 5, 7, 12, 0, 5)
    assert run.finished_at.tzinfo is None


def test_mark_run_failed_sets_error_and_duration_with_naive_started_at() -> None:
    run = ScheduledJobRun(job_id=1, status=ScheduledJobRunStatus.running)
    run.started_at = datetime(2026, 5, 1, 12, 0)
    repository = ScheduledJobRunRepository.__new__(ScheduledJobRunRepository)

    result = repository.apply_failure_state(run, error_message="job failed")

    assert result is run
    assert run.status == ScheduledJobRunStatus.failed
    assert run.error_message == "job failed"
    assert run.finished_at is not None
    assert run.finished_at.tzinfo is None
    assert run.duration_ms is not None
    assert run.duration_ms >= 0


def test_mark_run_succeeded_preserves_aware_started_at_timezone() -> None:
    run = ScheduledJobRun(job_id=1, status=ScheduledJobRunStatus.running)
    run.started_at = datetime(2026, 5, 7, 12, 0, tzinfo=UTC)
    repository = ScheduledJobRunRepository.__new__(ScheduledJobRunRepository)

    repository.apply_success_state(run, result={"processed": 1})

    assert run.finished_at is not None
    assert run.finished_at.tzinfo is not None


def test_mark_job_scheduled_updates_last_and_next_run() -> None:
    job = ScheduledJob()
    last_run_at = datetime(2026, 5, 7, 12, 0, tzinfo=UTC)
    next_run_at = datetime(2026, 5, 7, 12, 5, tzinfo=UTC)
    repository = ScheduledJobRepository.__new__(ScheduledJobRepository)

    result = repository.apply_schedule_state(
        job,
        last_run_at=last_run_at,
        next_run_at=next_run_at,
    )

    assert result is job
    assert job.last_run_at == last_run_at
    assert job.next_run_at == next_run_at
