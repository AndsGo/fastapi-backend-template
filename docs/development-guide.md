# Development Guide

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

## Configuration

Set `DATABASE_URL` in `.env`.

PostgreSQL:

```dotenv
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/app
```

MySQL 8.0:

```dotenv
DATABASE_URL=mysql+pymysql://app:app@localhost:3306/app?charset=utf8mb4
```

Set `REDIS_URL` when running distributed scheduler or worker processes.

## Start API

```bash
uvicorn app.main:app --reload
```

## Start Jobs

Scheduler:

```bash
python -m app.jobs.runner scheduler --interval-seconds 10 --scheduler-id scheduler-1
```

Worker:

```bash
python -m app.jobs.runner worker --interval-seconds 5 --worker-id worker-1 --max-workers 4
```

Both in one local process:

```bash
python -m app.jobs.runner all --interval-seconds 10 --max-workers 4
```

## Logs

Default runtime logs are JSON Lines on stdout.

Write to a local rotating file:

```powershell
$env:LOG_OUTPUT = "file"; $env:LOG_FILE_PATH = "logs/app.log"; python -m app.jobs.runner worker --once
```

Use both stdout and file:

```powershell
$env:LOG_OUTPUT = "both"; python -m app.jobs.runner worker --once
```

## Verify

```bash
python -m pytest
python -m ruff check .
lint-imports
python -m mypy app
```
