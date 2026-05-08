from typing import Any

from app.services.scheduled_job_service import ScheduledJobService


class ListScheduledJobRunsUseCase:
    def __init__(self, service: ScheduledJobService) -> None:
        self.service = service

    def execute(self, *, job_id: int, skip: int = 0, limit: int = 100) -> list[Any]:
        runs: list[Any] = self.service.list_runs(job_id=job_id, skip=skip, limit=limit)
        return runs
