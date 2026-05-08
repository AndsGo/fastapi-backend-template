from typing import Any

from app.services.scheduled_job_service import ScheduledJobService


class GetScheduledJobUseCase:
    def __init__(self, service: ScheduledJobService) -> None:
        self.service = service

    def execute(self, job_id: int) -> Any:
        return self.service.get_job(job_id)
