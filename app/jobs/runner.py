from __future__ import annotations

import argparse
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy.orm import Session

from app.cache.redis import get_redis_client
from app.core.logging import configure_logging
from app.db.session import get_session_local
from app.jobs.handlers.example import router as example_job_router
from app.jobs.locks import RedisLockClient
from app.jobs.logging import (
    log_scheduler_started,
    log_scheduler_tick_finished,
    log_scheduler_tick_started,
    log_worker_started,
    log_worker_tick_finished,
    log_worker_tick_started,
)
from app.jobs.registry import JobRegistry
from app.jobs.run_worker import ConcurrentScheduledRunWorker
from app.jobs.scheduler import DistributedScheduler
from app.repositories.scheduled_job_repository import (
    ScheduledJobRepository,
    ScheduledJobRunRepository,
)


def build_job_registry(session: Session) -> JobRegistry:
    registry = JobRegistry()
    registry.include_router(example_job_router)
    return registry


def build_scheduler(session: Any, *, scheduler_id: str) -> DistributedScheduler:
    return DistributedScheduler(
        job_repository=ScheduledJobRepository(session),
        run_repository=ScheduledJobRunRepository(session),
        redis_client=cast(RedisLockClient, get_redis_client()),
        scheduler_id=scheduler_id,
    )


def build_run_worker(
    *,
    session_factory: Callable[[], Session],
    worker_id: str,
    max_workers: int,
    lock_ttl_seconds: int = 300,
) -> ConcurrentScheduledRunWorker:
    return ConcurrentScheduledRunWorker(
        session_factory=session_factory,
        run_repository_factory=ScheduledJobRunRepository,
        registry=build_job_registry,
        redis_client=cast(RedisLockClient, get_redis_client()),
        worker_id=worker_id,
        max_workers=max_workers,
        lock_ttl_seconds=lock_ttl_seconds,
    )


def run_scheduler_once(*, scheduler_id: str, limit: int) -> dict[str, int]:
    session_factory = get_session_local()
    session = session_factory()
    try:
        scheduler = build_scheduler(session, scheduler_id=scheduler_id)
        return scheduler.run_once(now=datetime.now(UTC), limit=limit)
    finally:
        session.close()


def run_worker_once(
    *,
    worker_id: str,
    limit: int,
    max_workers: int,
    lock_ttl_seconds: int,
) -> dict[str, int]:
    worker = build_run_worker(
        session_factory=get_session_local(),
        worker_id=worker_id,
        max_workers=max_workers,
        lock_ttl_seconds=lock_ttl_seconds,
    )
    return worker.run_once(now=datetime.now(UTC), limit=limit)


def run_loop(args: argparse.Namespace) -> None:
    if args.mode in {"scheduler", "all"}:
        log_scheduler_started(scheduler_id=args.scheduler_id)
    if args.mode in {"worker", "all"}:
        log_worker_started(worker_id=args.worker_id, max_workers=args.max_workers)

    while True:
        if args.mode in {"scheduler", "all"}:
            log_scheduler_tick_started(
                scheduler_id=args.scheduler_id,
                limit=args.scheduler_limit,
            )
            scheduler_result = run_scheduler_once(
                scheduler_id=args.scheduler_id,
                limit=args.scheduler_limit,
            )
            log_scheduler_tick_finished(
                scheduler_id=args.scheduler_id,
                **scheduler_result,
            )

        if args.mode in {"worker", "all"}:
            log_worker_tick_started(
                worker_id=args.worker_id,
                limit=args.worker_limit,
                max_workers=args.max_workers,
            )
            worker_result = run_worker_once(
                worker_id=args.worker_id,
                limit=args.worker_limit,
                max_workers=args.max_workers,
                lock_ttl_seconds=args.lock_ttl_seconds,
            )
            log_worker_tick_finished(worker_id=args.worker_id, **worker_result)

        if args.once:
            return

        time.sleep(args.interval_seconds)


def parse_args_from_list(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run backend job scheduler or worker.")
    parser.add_argument("mode", choices=["scheduler", "worker", "all"])
    parser.add_argument("--once", action="store_true", help="Run one iteration and exit.")
    parser.add_argument("--interval-seconds", type=float, default=10.0)
    parser.add_argument("--scheduler-id", default="scheduler-1")
    parser.add_argument("--worker-id", default="worker-1")
    parser.add_argument("--scheduler-limit", type=int, default=100)
    parser.add_argument("--worker-limit", type=int, default=100)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--lock-ttl-seconds", type=int, default=300)
    return parser.parse_args(argv)


def parse_args() -> argparse.Namespace:
    return parse_args_from_list()


def main() -> None:
    configure_logging()
    run_loop(parse_args())


if __name__ == "__main__":
    main()
