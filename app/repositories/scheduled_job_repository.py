from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Select, or_, select, update

from app.domains.enums import ScheduledJobRunStatus, ScheduledJobStatus
from app.models.scheduled_job import ScheduledJob
from app.models.scheduled_job_run import ScheduledJobRun
from app.repositories.base import SQLAlchemyRepository


def _finished_at_for(started_at: datetime | None) -> datetime:
    if started_at is None:
        return datetime.now(UTC)
    if started_at.tzinfo is None:
        return datetime.now(UTC).replace(tzinfo=None)
    return datetime.now(started_at.tzinfo)


class ScheduledJobRepository(SQLAlchemyRepository[ScheduledJob]):
    model = ScheduledJob

    @staticmethod
    def due_jobs_statement(now: datetime, limit: int = 100) -> Select[tuple[ScheduledJob]]:
        return (
            select(ScheduledJob)
            .where(
                ScheduledJob.status == ScheduledJobStatus.enabled,
                or_(ScheduledJob.next_run_at.is_(None), ScheduledJob.next_run_at <= now),
            )
            .order_by(ScheduledJob.next_run_at.nulls_first(), ScheduledJob.id)
            .limit(limit)
        )

    def list_due_jobs(self, now: datetime, limit: int = 100) -> list[ScheduledJob]:
        statement = self.due_jobs_statement(now, limit=limit)
        return list(self.db.scalars(statement).all())

    @staticmethod
    def refresh_for_execution_statement(job_id: int) -> Select[tuple[ScheduledJob]]:
        return select(ScheduledJob).where(ScheduledJob.id == job_id).execution_options(
            populate_existing=True,
        )

    def refresh_for_execution(self, job_id: int) -> ScheduledJob | None:
        statement = self.refresh_for_execution_statement(job_id)
        return self.db.scalar(statement)

    def apply_schedule_state(
        self,
        job: ScheduledJob,
        *,
        last_run_at: datetime,
        next_run_at: datetime | None,
    ) -> ScheduledJob:
        job.last_run_at = last_run_at
        job.next_run_at = next_run_at
        return job


class ScheduledJobRunRepository(SQLAlchemyRepository[ScheduledJobRun]):
    model = ScheduledJobRun

    def list_by_job(self, job_id: int, skip: int = 0, limit: int = 100) -> list[ScheduledJobRun]:
        statement = (
            select(ScheduledJobRun)
            .where(ScheduledJobRun.job_id == job_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    @staticmethod
    def runnable_runs_statement(now: datetime, limit: int = 100) -> Select[tuple[ScheduledJobRun]]:
        return (
            select(ScheduledJobRun)
            .where(ScheduledJobRun.status == ScheduledJobRunStatus.pending)
            .where(
                or_(
                    ScheduledJobRun.locked_until.is_(None),
                    ScheduledJobRun.locked_until <= now,
                )
            )
            .order_by(ScheduledJobRun.created_at.asc(), ScheduledJobRun.id.asc())
            .limit(limit)
        )

    def list_runnable_runs(self, now: datetime, limit: int = 100) -> list[ScheduledJobRun]:
        statement = self.runnable_runs_statement(now, limit=limit)
        return list(self.db.scalars(statement).all())

    @staticmethod
    def claim_run_running_statement(
        run_id: int,
        *,
        worker_id: str,
        locked_until: datetime,
        now: datetime,
    ) -> Any:
        return (
            update(ScheduledJobRun)
            .where(ScheduledJobRun.id == run_id)
            .where(ScheduledJobRun.status == ScheduledJobRunStatus.pending)
            .where(
                or_(
                    ScheduledJobRun.locked_until.is_(None),
                    ScheduledJobRun.locked_until <= now,
                )
            )
            .values(
                status=ScheduledJobRunStatus.running,
                worker_id=worker_id,
                locked_until=locked_until,
                started_at=now,
                heartbeat_at=now,
            )
            .returning(ScheduledJobRun.id)
        )

    def claim_run_running(
        self,
        run_id: int,
        *,
        worker_id: str,
        locked_until: datetime,
        now: datetime,
    ) -> ScheduledJobRun | None:
        claimed_run_id = self.db.execute(
            self.claim_run_running_statement(
                run_id,
                worker_id=worker_id,
                locked_until=locked_until,
                now=now,
            )
        ).scalar_one_or_none()
        if claimed_run_id is None:
            return None

        self.db.commit()
        return self.db.get(ScheduledJobRun, claimed_run_id)

    def apply_running_state(
        self,
        run: ScheduledJobRun,
        *,
        worker_id: str,
    ) -> ScheduledJobRun:
        now = datetime.now(UTC)
        run.status = ScheduledJobRunStatus.running
        run.worker_id = worker_id
        run.started_at = now
        run.heartbeat_at = now
        return run

    def apply_success_state(
        self,
        run: ScheduledJobRun,
        *,
        result: dict[str, Any],
    ) -> ScheduledJobRun:
        finished_at = _finished_at_for(run.started_at)
        run.status = ScheduledJobRunStatus.succeeded
        run.finished_at = finished_at
        run.result = result
        if run.started_at is not None:
            run.duration_ms = int((finished_at - run.started_at).total_seconds() * 1000)
        return run

    def apply_failure_state(
        self,
        run: ScheduledJobRun,
        *,
        error_message: str,
    ) -> ScheduledJobRun:
        finished_at = _finished_at_for(run.started_at)
        run.status = ScheduledJobRunStatus.failed
        run.finished_at = finished_at
        run.error_message = error_message
        if run.started_at is not None:
            run.duration_ms = int((finished_at - run.started_at).total_seconds() * 1000)
        return run
