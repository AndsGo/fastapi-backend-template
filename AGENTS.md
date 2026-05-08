# AGENTS.md

## Project Context

This is a backend-only FastAPI framework template. It is intended to be reused by other projects as a baseline architecture.

## Rules For Agents

- Do not add frontend code unless explicitly requested.
- Do not add `docker-compose.yml` unless explicitly requested.
- Keep endpoints thin. Put behavior in services and database queries in repositories.
- Keep auth and permissions as placeholders until the stakeholder confirms the target SSO/OAuth2/RBAC design.
- Use environment variables for configuration. Do not hard-code credentials.
- Add or update tests for behavior changes.
- After completing a requirement, update the related documentation before final handoff.
- Run verification commands before claiming completion.

## Important Commands

```bash
python -m pytest
python -m ruff check .
python -m mypy app
uvicorn app.main:app --reload
alembic revision --autogenerate -m "message"
alembic upgrade head
```

