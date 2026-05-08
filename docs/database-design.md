# Database Design

The template supports PostgreSQL 13+ and MySQL 8.0+. The selected backend is configured with `DATABASE_URL`.

## Tables

Initial template tables:

- `audit_logs`: append-only operation records.
- `example_items`: neutral example module table.
- `scheduled_jobs`: recurring job definitions.
- `scheduled_job_runs`: job trigger and execution history.

## Compatibility Rules

- PostgreSQL URL: `postgresql+psycopg://user:password@host:5432/db`.
- MySQL URL: `mysql+pymysql://user:password@host:3306/db?charset=utf8mb4`.
- MySQL URLs must include `charset=utf8mb4`; engine creation fails fast otherwise.
- Engines use `READ COMMITTED` explicitly.
- MySQL `pool_recycle=3600` is intentional and shorter than common server-side idle timeouts.
- Unique string business keys use `app.db.types.case_sensitive_string()`.
- Persisted datetimes are UTC.
- Shared migrations should use portable SQLAlchemy types.
- Do not use PostgreSQL-only types such as `JSONB`, `ARRAY`, or `UUID` in common migrations unless dialect guarded and documented.

## Migrations

Generate migration:

```bash
alembic revision --autogenerate -m "message"
```

Apply migration:

```bash
alembic upgrade head
```

Check state:

```bash
python -m alembic heads --verbose
python -m alembic current --verbose
```

The template starts with one initial revision: `20260508_0001`.
