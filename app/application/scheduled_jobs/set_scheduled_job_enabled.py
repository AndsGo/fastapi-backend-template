from typing import Any

from app.services.scheduled_job_service import ScheduledJobService


class SetScheduledJobEnabledUseCase:
    def __init__(self, service: ScheduledJobService) -> None:
        self.service = service

    def execute(self, job_id: int, *, enabled: bool) -> Any:
        if enabled:
            return self.service.enable_job(job_id)
        return self.service.disable_job(job_id)
