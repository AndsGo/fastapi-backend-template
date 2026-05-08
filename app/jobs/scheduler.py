from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.cache.keys import RedisKey, build_cache_key
from app.domains.enums import ScheduledJobRunStatus, ScheduledJobStatus
from app.jobs.cron import next_cron_run_after
from app.jobs.locks import RedisDistributedLock, RedisLockClient
from app.jobs.logging import log_scheduler_job_failed, log_scheduler_job_triggered


class DistributedScheduler:
    def __init__(
        self,
        job_repository: Any,
        run_repository: Any,
        redis_client: RedisLockClient,
        scheduler_id: str,
    ) -> None:
        self.job_repository = job_repository
        self.run_repository = run_repository
        self.redis_client = redis_client
        self.scheduler_id = scheduler_id

    def run_once(self, now: datetime | None = None, limit: int = 100) -> dict[str, int]:
        selected_now = now or datetime.now(UTC)
        jobs = self.job_repository.list_due_jobs(selected_now, limit=limit)
        result = {"scanned": len(jobs), "triggered": 0, "skipped_locked": 0, "failed": 0}

        for job in jobs:
            lock_key = build_cache_key(RedisKey.SCHEDULED_JOB_LOCK, job_id=job.id)
            owner_token = f"{self.scheduler_id}:{job.id}:{uuid4().hex}"
            lock_ttl_seconds = max(
                job.lock_ttl_seconds,
                getattr(job, "max_runtime_seconds", job.lock_ttl_seconds),
            )
            lock = RedisDistributedLock(
                self.redis_client,
                key=lock_key,
                owner_token=owner_token,
                ttl_seconds=lock_ttl_seconds,
            )
            if not lock.acquire():
                result["skipped_locked"] += 1
                continue

            try:
                refresh_for_execution = getattr(self.job_repository, "refresh_for_execution", None)
                if callable(refresh_for_execution):
                    current_job = refresh_for_execution(job.id)
                else:
                    get_job = getattr(self.job_repository, "get", None)
                    current_job = get_job(job.id) if callable(get_job) else job
                if not self._is_runnable_job(current_job, selected_now):
                    result["skipped_locked"] += 1
                    continue

                try:
                    triggered = self._trigger_job(current_job, selected_now)
                except Exception as exc:
                    self._rollback_state_changes()
                    log_scheduler_job_failed(
                        exc,
                        scheduler_id=self.scheduler_id,
                        job_id=current_job.id,
                        job_code=current_job.code,
                        job_type=current_job.job_type,
                    )
                    result["failed"] += 1
                    continue

                if triggered:
                    log_scheduler_job_triggered(
                        scheduler_id=self.scheduler_id,
                        job_id=current_job.id,
                        job_code=current_job.code,
                        job_type=current_job.job_type,
                    )
                    result["triggered"] += 1
                else:
                    result["failed"] += 1
            finally:
                lock.release()

        return result

    def _is_runnable_job(self, job: Any | None, now: datetime) -> bool:
        if job is None:
            return False
        if getattr(job, "status", None) != ScheduledJobStatus.enabled:
            return False
        next_run_at = getattr(job, "next_run_at", None)
        return next_run_at is None or _is_due_at(next_run_at, now)

    def _trigger_job(self, job: Any, now: datetime) -> bool:
        next_run_at = next_cron_run_after(job.cron_expression, job.timezone, now)

        self.run_repository.create(
            {
                "job_id": job.id,
                "status": ScheduledJobRunStatus.pending,
                "triggered_by": self.scheduler_id,
                "trigger_info": {
                    "source": "scheduler",
                    "scheduler_id": self.scheduler_id,
                    "scheduled_job_id": job.id,
                    "scheduled_job_code": job.code,
                    "scheduled_at": now.isoformat(),
                },
            }
        )
        self.job_repository.apply_schedule_state(job, last_run_at=now, next_run_at=next_run_at)
        self._commit_state_changes()
        return True

    def _commit_state_changes(self) -> None:
        db = getattr(self.job_repository, "db", None) or getattr(self.run_repository, "db", None)
        commit = getattr(db, "commit", None)
        if callable(commit):
            commit()

    def _rollback_state_changes(self) -> None:
        db = getattr(self.job_repository, "db", None) or getattr(self.run_repository, "db", None)
        rollback = getattr(db, "rollback", None)
        if callable(rollback):
            rollback()


def _is_due_at(next_run_at: datetime, now: datetime) -> bool:
    if next_run_at.tzinfo is None and now.tzinfo is not None:
        return next_run_at <= now.replace(tzinfo=None)
    if next_run_at.tzinfo is not None and now.tzinfo is None:
        return next_run_at.replace(tzinfo=None) <= now
    return next_run_at <= now
