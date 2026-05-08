from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.audit_logs.list_audit_logs import ListAuditLogsUseCase
from app.application.examples.create_example_item import CreateExampleItemUseCase
from app.application.examples.get_example_item import GetExampleItemUseCase
from app.application.examples.list_example_items import ListExampleItemsUseCase
from app.application.examples.update_example_item import UpdateExampleItemUseCase
from app.application.scheduled_jobs.create_scheduled_job import CreateScheduledJobUseCase
from app.application.scheduled_jobs.create_scheduled_job_run import CreateScheduledJobRunUseCase
from app.application.scheduled_jobs.get_scheduled_job import GetScheduledJobUseCase
from app.application.scheduled_jobs.list_scheduled_job_runs import ListScheduledJobRunsUseCase
from app.application.scheduled_jobs.list_scheduled_jobs import ListScheduledJobsUseCase
from app.application.scheduled_jobs.set_scheduled_job_enabled import SetScheduledJobEnabledUseCase
from app.application.scheduled_jobs.update_scheduled_job import UpdateScheduledJobUseCase
from app.db.session import get_db
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.example_repository import ExampleItemRepository
from app.repositories.scheduled_job_repository import (
    ScheduledJobRepository,
    ScheduledJobRunRepository,
)
from app.services.audit_log_service import AuditLogService
from app.services.example_service import ExampleItemService
from app.services.scheduled_job_service import ScheduledJobService


def get_example_item_service(db: Session = Depends(get_db)) -> ExampleItemService:
    return ExampleItemService(ExampleItemRepository(db))


def get_list_example_items_use_case(
    service: ExampleItemService = Depends(get_example_item_service),
) -> ListExampleItemsUseCase:
    return ListExampleItemsUseCase(service)


def get_create_example_item_use_case(
    service: ExampleItemService = Depends(get_example_item_service),
) -> CreateExampleItemUseCase:
    return CreateExampleItemUseCase(service)


def get_get_example_item_use_case(
    service: ExampleItemService = Depends(get_example_item_service),
) -> GetExampleItemUseCase:
    return GetExampleItemUseCase(service)


def get_update_example_item_use_case(
    service: ExampleItemService = Depends(get_example_item_service),
) -> UpdateExampleItemUseCase:
    return UpdateExampleItemUseCase(service)


def get_audit_log_service(db: Session = Depends(get_db)) -> AuditLogService:
    return AuditLogService(AuditLogRepository(db))


def get_list_audit_logs_use_case(
    service: AuditLogService = Depends(get_audit_log_service),
) -> ListAuditLogsUseCase:
    return ListAuditLogsUseCase(service)


def get_scheduled_job_service(db: Session = Depends(get_db)) -> ScheduledJobService:
    return ScheduledJobService(ScheduledJobRepository(db), ScheduledJobRunRepository(db))


def get_list_scheduled_jobs_use_case(
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> ListScheduledJobsUseCase:
    return ListScheduledJobsUseCase(service)


def get_create_scheduled_job_use_case(
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> CreateScheduledJobUseCase:
    return CreateScheduledJobUseCase(service)


def get_get_scheduled_job_use_case(
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> GetScheduledJobUseCase:
    return GetScheduledJobUseCase(service)


def get_update_scheduled_job_use_case(
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> UpdateScheduledJobUseCase:
    return UpdateScheduledJobUseCase(service)


def get_set_scheduled_job_enabled_use_case(
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> SetScheduledJobEnabledUseCase:
    return SetScheduledJobEnabledUseCase(service)


def get_list_scheduled_job_runs_use_case(
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> ListScheduledJobRunsUseCase:
    return ListScheduledJobRunsUseCase(service)


def get_create_scheduled_job_run_use_case(
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> CreateScheduledJobRunUseCase:
    return CreateScheduledJobRunUseCase(service)
