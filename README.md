# FastAPI Backend Template

Reusable backend-only FastAPI template for modular monolith services.

## Requirements

- Python 3.11 or newer.
- PostgreSQL or MySQL when running the persistence layer.
- Redis when running distributed scheduled jobs or Redis-backed cache features.

## What Is Included

- FastAPI API versioning and dependency injection.
- SQLAlchemy models, repositories, sessions, and Alembic migrations.
- PostgreSQL and MySQL support through `DATABASE_URL`.
- Redis client and centralized Redis key templates.
- Scheduled job definitions, scheduler, concurrent worker, and job registry.
- Runtime JSON logging to stdout and optional rotating local files.
- Thin API, service, repository, model, schema layering.
- A small `examples` module that demonstrates the expected structure.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

Set `DATABASE_URL` in `.env` for your database. Redis is optional unless you run
distributed jobs.

Key environment variables:

- `APP_ENV`: runtime environment name, such as `local`, `staging`, or `production`.
- `DATABASE_URL`: SQLAlchemy database URL for PostgreSQL or MySQL.
- `SECRET_KEY`: application secret used by security helpers; replace the example value.
- `BACKEND_CORS_ORIGINS`: JSON array of allowed browser origins.
- `REDIS_URL`: Redis connection URL for cache and distributed job coordination.
- `REDIS_PREFIX`: prefix applied to Redis keys owned by this application.

## Database Migrations

```bash
alembic upgrade head
```

Create new migrations after model changes:

```bash
alembic revision --autogenerate -m "describe change"
```

## Run API

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Run Jobs

```bash
python -m app.jobs.runner scheduler --interval-seconds 10
python -m app.jobs.runner worker --interval-seconds 5 --worker-id worker-1 --max-workers 4
```

Installed console script:

```bash
backend-jobs worker --once --max-workers 4
```

## Verify

```bash
python -m pytest
python -m ruff check .
python -m mypy app
```

## Use As A Template

Use the existing `examples` module as the reference implementation when adding a new
business area:

- Add database models under `app/models`.
- Add request and response schemas under `app/schemas`.
- Put database access in `app/repositories`.
- Put business behavior in `app/services` or `app/application`.
- Expose HTTP routes from `app/api/v1/endpoints` and register them in the v1 router.
- Add tests in `tests` for repositories, services, application use cases, and endpoints.
- Update the related documentation under `docs`.

The project intentionally keeps authentication and authorization as placeholders. Confirm
the target SSO, OAuth2, or RBAC design before using this template for production access
control.

## Continuous Integration

GitHub Actions runs the same verification commands on pushes and pull requests to `main`.

## Main Docs

- [Architecture](docs/architecture.md)
- [Development guide](docs/development-guide.md)
- [Database design](docs/database-design.md)
- [Job guide](docs/job-guide.md)
- [Project framework standards](docs/project-framework-standards.md)
