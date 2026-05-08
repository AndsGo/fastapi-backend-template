from typing import Any

from app.schemas.scheduled_job import ScheduledJobUpdate
from app.services.scheduled_job_service import ScheduledJobService


class UpdateScheduledJobUseCase:
    def __init__(self, service: ScheduledJobService) -> None:
        self.service = service

    def execute(self, job_id: int, payload: ScheduledJobUpdate) -> Any:
        return self.service.update_job(job_id, payload)
