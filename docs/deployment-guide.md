# Deployment Guide

This template does not include container orchestration by default.

## API Process

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Job Processes

```bash
python -m app.jobs.runner scheduler --interval-seconds 10
python -m app.jobs.runner worker --interval-seconds 5 --worker-id worker-1 --max-workers 4
```

Run scheduler and worker as separate processes in prod.

## Required Configuration

- `DATABASE_URL`
- `SECRET_KEY`
- `BACKEND_CORS_ORIGINS`

Optional:

- `REDIS_URL`
- `REDIS_PREFIX`
- `LOG_OUTPUT`
- `LOG_FILE_PATH`

Prefer stdout JSON logs in container or process-manager environments.

