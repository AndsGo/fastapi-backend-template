# Job Guide

The job system is generic infrastructure for work that should not run directly inside HTTP requests.

## Runtime Pieces

- `scheduled_jobs`: recurring job definitions.
- `scheduled_job_runs`: trigger and execution records.
- `DistributedScheduler`: scans due jobs and creates pending runs.
- `ConcurrentScheduledRunWorker`: claims pending runs and executes handlers with thread-pool concurrency.
- `app/jobs/handlers`: delivery adapters for scheduled runs.
- `JobRouter`: decorator-style handler registration.
- `JobRegistry`: runtime handler lookup and execution.
- Redis: distributed locks and heartbeats.

## Register A Job

Create an application use case:

```python
from app.jobs.registry import JobContext, JobResult

class RunNoopJobUseCase:
    def execute(self, context: JobContext) -> JobResult:
        return JobResult(processed_count=1, succeeded_count=1)
```

Expose it through a job handler adapter:

```python
from app.application.examples.run_noop_job import RunNoopJobUseCase
from app.jobs.registry import JobContext, JobResult, JobRouter

router = JobRouter()

@router.handler("example.noop")
def noop(context: JobContext) -> JobResult:
    return RunNoopJobUseCase().execute(context)
```

Include the router in `app/jobs/runner.py` inside `build_job_registry()`.

Handlers must accept `JobContext` and return `JobResult`.

## Run Manually

```bash
python -m app.jobs.runner scheduler --once
python -m app.jobs.runner worker --once --max-workers 4
```

## Design Rules

- The scheduler only creates due runs; it does not execute business behavior.
- The worker only claims runs and dispatches handlers.
- Each worker task gets its own SQLAlchemy session.
- Job handlers are delivery adapters and should call application use cases.
- Application use cases own domain behavior orchestration and may call services/repositories.
- Use Redis for locks and coordination, not as the source of truth.
- Database rows remain the source of truth for definitions and run history.
