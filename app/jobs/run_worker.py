from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from app.cache.keys import RedisKey, build_cache_key
from app.jobs.locks import RedisDistributedLock, RedisLockClient
from app.jobs.logging import (
    log_worker_run_claimed,
    log_worker_run_executed,
    log_worker_run_failed,
)
from app.jobs.registry import JobContext, JobRegistry

JobRegistryFactory = Callable[[Any], JobRegistry]
LogCall = Callable[[], None]


class ConcurrentScheduledRunWorker:
    def __init__(
        self,
        session_factory: Callable[[], Any],
        run_repository_factory: Callable[[Any], Any],
        registry: JobRegistry | JobRegistryFactory,
        redis_client: RedisLockClient,
        worker_id: str,
        max_workers: int = 4,
        lock_ttl_seconds: int = 300,
    ) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be greater than or equal to 1")

        self.session_factory = session_factory
        self.run_repository_factory = run_repository_factory
        self.registry = registry
        self.redis_client = redis_client
        self.worker_id = worker_id
        self.max_workers = max_workers
        self.lock_ttl_seconds = lock_ttl_seconds

    def run_once(self, now: datetime | None = None, limit: int = 100) -> dict[str, int]:
        selected_now = now or datetime.now(UTC)
        run_ids = self._list_runnable_run_ids(selected_now, limit=limit)
        result = {"scanned": len(run_ids), "executed": 0, "skipped_locked": 0, "failed": 0}

        if not run_ids:
            return result

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self._execute_one, run_id, selected_now) for run_id in run_ids
            ]
            for future in as_completed(futures):
                status = future.result()
                result[status] += 1

        return result

    def _list_runnable_run_ids(self, now: datetime, *, limit: int) -> list[int]:
        session = self.session_factory()
        try:
            repository = self.run_repository_factory(session)
            runs = repository.list_runnable_runs(now, limit=limit)
            return [run.id for run in runs]
        finally:
            session.close()

    def _execute_one(self, run_id: int, now: datetime) -> str:
        lock_key = build_cache_key(RedisKey.SCHEDULED_RUN_LOCK, run_id=run_id)
        owner_token = f"{self.worker_id}:{run_id}:{uuid4().hex}"
        lock = RedisDistributedLock(
            self.redis_client,
            key=lock_key,
            owner_token=owner_token,
            ttl_seconds=self.lock_ttl_seconds,
        )
        if not lock.acquire():
            return "skipped_locked"

        session = self.session_factory()
        run: Any | None = None
        claimed_run_id: int | None = None
        claimed_job_id: int | None = None
        claimed_job_type: str | None = None
        try:
            repository = self.run_repository_factory(session)
            locked_until = now + timedelta(seconds=self.lock_ttl_seconds)
            run = repository.claim_run_running(
                run_id,
                worker_id=self.worker_id,
                locked_until=locked_until,
                now=now,
            )
            if run is None:
                self._commit_state_changes(repository)
                return "skipped_locked"

            claimed_run_id = run.id
            claimed_job_id = run.job_id
            claimed_job_type = run.job.job_type
            claimed_payload = run.job.payload or {}
            claimed_triggered_by = run.triggered_by

            self._commit_state_changes(repository)
            _safe_log(
                lambda: log_worker_run_claimed(
                    worker_id=self.worker_id,
                    run_id=claimed_run_id,
                    job_id=claimed_job_id,
                    job_type=claimed_job_type,
                )
            )
            context = JobContext(
                job_id=claimed_job_id,
                run_id=claimed_run_id,
                job_type=claimed_job_type,
                payload=claimed_payload,
                triggered_by=claimed_triggered_by,
                worker_id=self.worker_id,
                db=session,
                redis=self.redis_client,
            )
            job_result = self._registry_for_session(session).execute(context)
            result_payload = asdict(job_result)
            repository.apply_success_state(run, result=result_payload)
            self._commit_state_changes(repository)
            _safe_log(
                lambda: log_worker_run_executed(
                    worker_id=self.worker_id,
                    run_id=claimed_run_id,
                    job_id=claimed_job_id,
                    job_type=claimed_job_type,
                    result=result_payload,
                )
            )
            return "executed"
        except Exception as exc:
            if (
                run is not None
                and claimed_run_id is not None
                and claimed_job_id is not None
                and claimed_job_type is not None
            ):
                repository.apply_failure_state(run, error_message=str(exc))
                self._commit_state_changes(repository)
                caught_exc = exc

                def log_failed() -> None:
                    log_worker_run_failed(
                        caught_exc,
                        worker_id=self.worker_id,
                        run_id=claimed_run_id,
                        job_id=claimed_job_id,
                        job_type=claimed_job_type,
                    )

                _safe_log(log_failed)
            return "failed"
        finally:
            session.close()
            lock.release()

    def _commit_state_changes(self, repository: Any) -> None:
        db = getattr(repository, "db", None)
        commit = getattr(db, "commit", None)
        if callable(commit):
            commit()

    def _registry_for_session(self, session: Any) -> JobRegistry:
        if isinstance(self.registry, JobRegistry):
            return self.registry
        return self.registry(session)


def _safe_log(log_call: LogCall) -> None:
    try:
        log_call()
    except Exception:
        return
