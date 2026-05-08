from typing import Any

from app.schemas.scheduled_job import ScheduledJobCreate
from app.services.scheduled_job_service import ScheduledJobService


class CreateScheduledJobUseCase:
    def __init__(self, service: ScheduledJobService) -> None:
        self.service = service

    def execute(self, payload: ScheduledJobCreate) -> Any:
        return self.service.create_job(payload)
