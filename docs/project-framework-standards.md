# Project Framework Standards

This document defines the reusable backend framework standards for projects based on this template.

## Scope

Use this template for backend-only FastAPI services that need a modular monolith structure, relational database migrations, optional Redis, scheduled jobs, structured logging, tests, linting, and type checking.

## Standard Structure

```text
app/
  api/
    v1/
      endpoints/
      dependencies.py
      router.py
  cache/
    keys.py
    redis.py
  core/
    config.py
    exceptions.py
    logging.py
    security.py
  db/
    migrations/
    base.py
    engine.py
    session.py
    types.py
  domains/
    enums.py
  application/
    dto/
    examples/
  jobs/
    cron.py
    locks.py
    logging.py
    registry.py
    run_worker.py
    runner.py
    scheduler.py
    handlers/
  models/
  repositories/
  schemas/
  services/
tests/
docs/
```

## Layering Rules

Allowed direction:

```text
api -> application
jobs/handlers -> application
application -> services
application -> repositories
application -> domains
services -> repositories
services -> domains
repositories -> models
```

Forbidden direction:

```text
models -> services
models -> api
repositories -> api
endpoints -> database queries
api -> multiple services directly
jobs/handlers -> multiple services directly
services -> services
```

## Automated Architecture Gate

The dependency rules are enforced by Import Linter in `.importlinter`.

CI rejects direct imports that violate these boundaries:

- API modules must not import services, repositories, models, or `app.db` directly.
- Job handlers must not import services, repositories, models, `app.db`, or API modules directly.
- Services must not import other services.
- Repositories must not import API, application, services, or jobs.
- Models must not import upper layers.

Run the architecture gate locally:

```bash
lint-imports
```

## Adding A Module

1. Add model in `app/models`.
2. Add schemas in `app/schemas`.
3. Add repository in `app/repositories`.
4. Add atomic service in `app/services`.
5. Add DTOs and use cases in `app/application`.
6. Add endpoint in `app/api/v1/endpoints`.
7. Register endpoint in `app/api/v1/router.py`.
8. Add job handlers in `app/jobs/handlers` if needed.
9. Add migration.
10. Add tests.
11. Update docs.

Use `ExampleItem` as the reference implementation.

## Jobs

- Job definitions live in `scheduled_jobs`.
- Run history lives in `scheduled_job_runs`.
- Handlers are registered with `JobRouter`.
- Handler signature is `JobContext -> JobResult`.
- Scheduler and worker are infrastructure.
- Job handlers are delivery adapters and should call application use cases.
- Cross-module orchestration belongs in `app/application`, not in handlers or endpoints.

## Application Layer

`app/application` is the DDD application layer.

Responsibilities:

- Use case orchestration.
- Non-HTTP input/output DTOs.
- Cross-module coordination.
- Transaction boundary ownership.
- Idempotency and permission checks when they are use-case concerns.

Rules:

- API schemas should be converted into application DTOs.
- Jobs should call application use cases.
- Application use cases may call multiple services and repositories.
- Services must remain atomic and must not call other services.
- Application code must not return FastAPI responses.

## Database

- `DATABASE_URL` selects PostgreSQL or MySQL.
- MySQL URLs must include `charset=utf8mb4`.
- Engine isolation is `READ COMMITTED`.
- Unique string business keys use `case_sensitive_string()`.
- Persisted datetimes are UTC.
- Migrations must be portable unless explicitly dialect guarded.

## Redis

- Redis key templates live in `app/cache/keys.py`.
- Use `build_cache_key()`.
- Do not scatter hard-coded Redis keys in services or endpoints.

## Logging

- Runtime logs are JSON Lines by default.
- Prefer stdout in prod.
- Local rotating file output is optional through `LOG_OUTPUT=file` or `LOG_OUTPUT=both`.
- Do not log secrets.

## Delivery Checklist

Before handoff:

```bash
python -m ruff check .
lint-imports
python -m mypy app
python -m pytest
```

Also check:

- `.env.example` is updated for new configuration.
- Migrations match model changes.
- Documentation reflects behavior changes.
- No real secrets are committed.

