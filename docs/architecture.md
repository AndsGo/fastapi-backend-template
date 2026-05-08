# Architecture

This project is a backend-only FastAPI modular monolith template.

## Layers

```text
HTTP request
  -> app/api
  -> app/application
  -> app/services
  -> app/repositories
  -> app/models
  -> database
```

Rules:

- API endpoints handle HTTP concerns, request parsing, response models, and dependency injection.
- Job handlers adapt scheduled runs into application use case calls.
- `app/application` owns use case orchestration, non-HTTP DTOs, transaction boundaries, and cross-module coordination.
- Services own atomic module capabilities and must not call other services.
- Repositories own SQLAlchemy queries and persistence details.
- Models define database tables only.
- Schemas define Pydantic request and response contracts.
- `app/core` owns settings, logging, exceptions, and security placeholders.
- `app/db` owns SQLAlchemy base, engine/session creation, type helpers, and Alembic.
- `app/cache` owns Redis client creation and key templates.
- `app/jobs` owns generic scheduler, worker, lock, registry, runner infrastructure, and handler adapters.

## Example Module

The example slice demonstrates the expected module structure:

```text
app/api/v1/endpoints/examples.py
app/application/dto/example.py
app/application/examples/create_example_item.py
app/application/examples/get_example_item.py
app/application/examples/list_example_items.py
app/application/examples/update_example_item.py
app/jobs/handlers/example.py
app/models/example.py
app/repositories/example_repository.py
app/schemas/example.py
app/services/example_service.py
```

Use it as a pattern when adding real modules, then replace or remove it in application projects.

## Extension Flow

1. Add domain enums or value objects only if they are framework independent.
2. Add a model in `app/models`.
3. Add schemas in `app/schemas`.
4. Add a repository in `app/repositories`.
5. Add an atomic service in `app/services`.
6. Add application DTOs and use cases in `app/application`.
7. Add endpoints in `app/api/v1/endpoints`.
8. Register routes in `app/api/v1/router.py`.
9. Add job handlers in `app/jobs/handlers` when background execution is needed.
10. Add Alembic migration and tests.
11. Update docs.

## DDD Dependency Rules

```text
api -> application
jobs/handlers -> application
application -> services
application -> repositories
application -> domains
services -> repositories
services -> domains
repositories -> models
domains -> no framework dependency
```

`api` and `jobs/handlers` are delivery adapters. They must not orchestrate multiple services directly.

`services` are atomic capability providers. They must not call other services. Cross-module workflows belong in `application`.
