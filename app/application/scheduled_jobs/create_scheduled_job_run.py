from typing import Any

from app.schemas.scheduled_job import ScheduledJobRunCreate
from app.services.scheduled_job_service import ScheduledJobService


class CreateScheduledJobRunUseCase:
    def __init__(self, service: ScheduledJobService) -> None:
        self.service = service

    def execute(self, job_id: int, payload: ScheduledJobRunCreate) -> Any:
        return self.service.create_run(job_id, payload)
