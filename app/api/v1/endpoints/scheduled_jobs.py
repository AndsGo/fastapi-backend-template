from typing import Any

from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import get_scheduled_job_service
from app.schemas.scheduled_job import (
    ScheduledJobCreate,
    ScheduledJobResponse,
    ScheduledJobRunCreate,
    ScheduledJobRunResponse,
    ScheduledJobUpdate,
)
from app.services.scheduled_job_service import ScheduledJobService

router = APIRouter()


@router.get("", response_model=list[ScheduledJobResponse])
def list_jobs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> list[Any]:
    return service.list_jobs(skip=skip, limit=limit)


@router.post("", response_model=ScheduledJobResponse, status_code=201)
def create_job(
    payload: ScheduledJobCreate,
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> Any:
    return service.create_job(payload)


@router.get("/{job_id}", response_model=ScheduledJobResponse)
def get_job(
    job_id: int,
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> Any:
    return service.get_job(job_id)


@router.patch("/{job_id}", response_model=ScheduledJobResponse)
def update_job(
    job_id: int,
    payload: ScheduledJobUpdate,
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> Any:
    return service.update_job(job_id, payload)


@router.post("/{job_id}/enable", response_model=ScheduledJobResponse)
def enable_job(
    job_id: int,
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> Any:
    return service.enable_job(job_id)


@router.post("/{job_id}/disable", response_model=ScheduledJobResponse)
def disable_job(
    job_id: int,
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> Any:
    return service.disable_job(job_id)


@router.get("/{job_id}/runs", response_model=list[ScheduledJobRunResponse])
def list_runs(
    job_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> list[Any]:
    return service.list_runs(job_id=job_id, skip=skip, limit=limit)


@router.post("/{job_id}/runs", response_model=ScheduledJobRunResponse, status_code=201)
def create_run(
    job_id: int,
    payload: ScheduledJobRunCreate,
    service: ScheduledJobService = Depends(get_scheduled_job_service),
) -> Any:
    return service.create_run(job_id, payload)
