from typing import Any

from app.services.scheduled_job_service import ScheduledJobService


class ListScheduledJobsUseCase:
    def __init__(self, service: ScheduledJobService) -> None:
        self.service = service

    def execute(self, *, skip: int = 0, limit: int = 100) -> list[Any]:
        jobs: list[Any] = self.service.list_jobs(skip=skip, limit=limit)
        return jobs
