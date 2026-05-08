from __future__ import annotations

from typing import Any

from app.core.logging import get_logger

logger = get_logger("app.jobs")


def log_scheduler_started(*, scheduler_id: str) -> None:
    logger.info(
        "Scheduler started",
        extra={
            "event": "scheduler.started",
            "component": "scheduler",
            "scheduler_id": scheduler_id,
        },
    )


def log_scheduler_tick_started(*, scheduler_id: str, limit: int) -> None:
    logger.info(
        "Scheduler tick started",
        extra={
            "event": "scheduler.tick_started",
            "component": "scheduler",
            "scheduler_id": scheduler_id,
            "limit": limit,
        },
    )


def log_scheduler_job_triggered(
    *,
    scheduler_id: str,
    job_id: int,
    job_code: str,
    job_type: str,
) -> None:
    logger.info(
        "Scheduled job triggered",
        extra={
            "event": "scheduler.job_triggered",
            "component": "scheduler",
            "scheduler_id": scheduler_id,
            "job_id": job_id,
            "job_code": job_code,
            "job_type": job_type,
        },
    )


def log_scheduler_job_failed(
    exc: BaseException,
    *,
    scheduler_id: str,
    job_id: int,
    job_code: str,
    job_type: str,
) -> None:
    logger.error(
        "Scheduled job trigger failed",
        extra={
            "event": "scheduler.job_failed",
            "component": "scheduler",
            "scheduler_id": scheduler_id,
            "job_id": job_id,
            "job_code": job_code,
            "job_type": job_type,
        },
        exc_info=(type(exc), exc, exc.__traceback__),
    )


def log_scheduler_tick_finished(
    *,
    scheduler_id: str,
    scanned: int,
    triggered: int,
    skipped_locked: int,
    failed: int,
) -> None:
    logger.info(
        "Scheduler tick finished",
        extra={
            "event": "scheduler.tick_finished",
            "component": "scheduler",
            "scheduler_id": scheduler_id,
            "scanned": scanned,
            "triggered": triggered,
            "skipped_locked": skipped_locked,
            "failed": failed,
        },
    )


def log_worker_started(*, worker_id: str, max_workers: int) -> None:
    logger.info(
        "Worker started",
        extra={
            "event": "worker.started",
            "component": "worker",
            "worker_id": worker_id,
            "max_workers": max_workers,
        },
    )


def log_worker_tick_started(*, worker_id: str, limit: int, max_workers: int) -> None:
    logger.info(
        "Worker tick started",
        extra={
            "event": "worker.tick_started",
            "component": "worker",
            "worker_id": worker_id,
            "limit": limit,
            "max_workers": max_workers,
        },
    )


def log_worker_run_claimed(
    *,
    worker_id: str,
    run_id: int,
    job_id: int,
    job_type: str,
) -> None:
    logger.info(
        "Scheduled run claimed",
        extra={
            "event": "worker.run_claimed",
            "component": "worker",
            "worker_id": worker_id,
            "run_id": run_id,
            "job_id": job_id,
            "job_type": job_type,
        },
    )


def log_worker_run_executed(
    *,
    worker_id: str,
    run_id: int,
    job_id: int,
    job_type: str,
    result: dict[str, Any],
) -> None:
    logger.info(
        "Scheduled run executed",
        extra={
            "event": "worker.run_executed",
            "component": "worker",
            "worker_id": worker_id,
            "run_id": run_id,
            "job_id": job_id,
            "job_type": job_type,
            "result": result,
        },
    )


def log_worker_run_failed(
    exc: BaseException,
    *,
    worker_id: str,
    run_id: int,
    job_id: int,
    job_type: str,
) -> None:
    logger.error(
        "Scheduled run failed",
        extra={
            "event": "worker.run_failed",
            "component": "worker",
            "worker_id": worker_id,
            "run_id": run_id,
            "job_id": job_id,
            "job_type": job_type,
        },
        exc_info=(type(exc), exc, exc.__traceback__),
    )


def log_worker_tick_finished(
    *,
    worker_id: str,
    scanned: int,
    executed: int,
    skipped_locked: int,
    failed: int,
) -> None:
    logger.info(
        "Worker tick finished",
        extra={
            "event": "worker.tick_finished",
            "component": "worker",
            "worker_id": worker_id,
            "scanned": scanned,
            "executed": executed,
            "skipped_locked": skipped_locked,
            "failed": failed,
        },
    )
