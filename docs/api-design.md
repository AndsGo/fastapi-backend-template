# API Design

All API routes are registered under `/api/v1`.

## Endpoint Rules

- Endpoints stay thin.
- Use Pydantic schemas for request and response contracts.
- Inject services through `app/api/v1/dependencies.py`.
- Put business behavior in services.
- Put database access in repositories.
- Return paginated lists for collection endpoints.

## Error Shape

Application exceptions are returned as:

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "message": "Resource not found",
  "details": {}
}
```

Use `app/core/exceptions.py` for reusable application errors.
