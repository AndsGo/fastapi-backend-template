from typing import Any

from app.core.exceptions import NotFoundError
from app.domains.enums import ScheduledJobRunStatus, ScheduledJobStatus
from app.schemas.scheduled_job import ScheduledJobCreate, ScheduledJobRunCreate, ScheduledJobUpdate


class ScheduledJobService:
    def __init__(self, job_repository: Any, run_repository: Any) -> None:
        self.job_repository = job_repository
        self.run_repository = run_repository

    def list_jobs(self, skip: int = 0, limit: int = 100) -> list[Any]:
        jobs: list[Any] = self.job_repository.list(skip=skip, limit=limit)
        return jobs

    def get_job(self, job_id: int) -> Any:
        job = self.job_repository.get(job_id)
        if job is None:
            raise NotFoundError("scheduled_job", job_id)
        return job

    def create_job(self, payload: ScheduledJobCreate) -> Any:
        data = payload.model_dump()
        data["status"] = ScheduledJobStatus.enabled
        data["last_run_at"] = None
        return self.job_repository.create(data)

    def update_job(self, job_id: int, payload: ScheduledJobUpdate) -> Any:
        job = self.get_job(job_id)
        return self.job_repository.update(job, payload.model_dump(exclude_unset=True))

    def enable_job(self, job_id: int) -> Any:
        job = self.get_job(job_id)
        return self.job_repository.update(job, {"status": ScheduledJobStatus.enabled})

    def disable_job(self, job_id: int) -> Any:
        job = self.get_job(job_id)
        return self.job_repository.update(job, {"status": ScheduledJobStatus.disabled})

    def list_runs(self, job_id: int, skip: int = 0, limit: int = 100) -> list[Any]:
        self.get_job(job_id)
        runs: list[Any] = self.run_repository.list_by_job(job_id, skip=skip, limit=limit)
        return runs

    def create_run(self, job_id: int, payload: ScheduledJobRunCreate) -> Any:
        self.get_job(job_id)
        data = payload.model_dump()
        data["job_id"] = job_id
        data["status"] = ScheduledJobRunStatus.pending
        return self.run_repository.create(data)
