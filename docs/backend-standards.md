# Backend Standards

## Layering

- API: HTTP protocol and dependency injection.
- Schema: Pydantic contracts.
- Service: use cases and orchestration.
- Repository: SQLAlchemy queries.
- Model: table definitions only.
- Core: configuration, logging, exceptions, security placeholders.

## Code Rules

- Keep endpoints thin.
- Do not query the database from endpoints.
- Do not import services from models.
- Do not read environment variables outside `app/core/config.py`.
- Add tests for behavior changes.
- Update related docs before handoff.

## Commands

```bash
python -m ruff check .
lint-imports
python -m mypy app
python -m pytest
```
