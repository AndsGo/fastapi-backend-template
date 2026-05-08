from typing import Any

from fastapi import APIRouter, Depends, Query

from app.application.providers import (
    get_create_scheduled_job_run_use_case,
    get_create_scheduled_job_use_case,
    get_get_scheduled_job_use_case,
    get_list_scheduled_job_runs_use_case,
    get_list_scheduled_jobs_use_case,
    get_set_scheduled_job_enabled_use_case,
    get_update_scheduled_job_use_case,
)
from app.application.scheduled_jobs.create_scheduled_job import CreateScheduledJobUseCase
from app.application.scheduled_jobs.create_scheduled_job_run import CreateScheduledJobRunUseCase
from app.application.scheduled_jobs.get_scheduled_job import GetScheduledJobUseCase
from app.application.scheduled_jobs.list_scheduled_job_runs import ListScheduledJobRunsUseCase
from app.application.scheduled_jobs.list_scheduled_jobs import ListScheduledJobsUseCase
from app.application.scheduled_jobs.set_scheduled_job_enabled import SetScheduledJobEnabledUseCase
from app.application.scheduled_jobs.update_scheduled_job import UpdateScheduledJobUseCase
from app.schemas.scheduled_job import (
    ScheduledJobCreate,
    ScheduledJobResponse,
    ScheduledJobRunCreate,
    ScheduledJobRunResponse,
    ScheduledJobUpdate,
)

router = APIRouter()


@router.get("", response_model=list[ScheduledJobResponse])
def list_jobs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    use_case: ListScheduledJobsUseCase = Depends(get_list_scheduled_jobs_use_case),
) -> list[Any]:
    return use_case.execute(skip=skip, limit=limit)


@router.post("", response_model=ScheduledJobResponse, status_code=201)
def create_job(
    payload: ScheduledJobCreate,
    use_case: CreateScheduledJobUseCase = Depends(get_create_scheduled_job_use_case),
) -> Any:
    return use_case.execute(payload)


@router.get("/{job_id}", response_model=ScheduledJobResponse)
def get_job(
    job_id: int,
    use_case: GetScheduledJobUseCase = Depends(get_get_scheduled_job_use_case),
) -> Any:
    return use_case.execute(job_id)


@router.patch("/{job_id}", response_model=ScheduledJobResponse)
def update_job(
    job_id: int,
    payload: ScheduledJobUpdate,
    use_case: UpdateScheduledJobUseCase = Depends(get_update_scheduled_job_use_case),
) -> Any:
    return use_case.execute(job_id, payload)


@router.post("/{job_id}/enable", response_model=ScheduledJobResponse)
def enable_job(
    job_id: int,
    use_case: SetScheduledJobEnabledUseCase = Depends(get_set_scheduled_job_enabled_use_case),
) -> Any:
    return use_case.execute(job_id, enabled=True)


@router.post("/{job_id}/disable", response_model=ScheduledJobResponse)
def disable_job(
    job_id: int,
    use_case: SetScheduledJobEnabledUseCase = Depends(get_set_scheduled_job_enabled_use_case),
) -> Any:
    return use_case.execute(job_id, enabled=False)


@router.get("/{job_id}/runs", response_model=list[ScheduledJobRunResponse])
def list_runs(
    job_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    use_case: ListScheduledJobRunsUseCase = Depends(get_list_scheduled_job_runs_use_case),
) -> list[Any]:
    return use_case.execute(job_id=job_id, skip=skip, limit=limit)


@router.post("/{job_id}/runs", response_model=ScheduledJobRunResponse, status_code=201)
def create_run(
    job_id: int,
    payload: ScheduledJobRunCreate,
    use_case: CreateScheduledJobRunUseCase = Depends(get_create_scheduled_job_run_use_case),
) -> Any:
    return use_case.execute(job_id, payload)
