# Testing Guide

Run the full suite:

```bash
python -m pytest
```

Run quality gates:

```bash
python -m ruff check .
python -m mypy app
```

Expected test groups:

- API smoke tests.
- Settings tests.
- Logging tests.
- Redis key tests.
- Database engine/type/migration tests.
- Service tests.
- Job scheduler/worker/registry tests.
- Example module tests.

Behavior changes should add or update tests before handoff.
