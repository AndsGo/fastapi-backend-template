from typing import Any

from app.schemas.audit_log import AuditLogCreate


class AuditLogService:
    def __init__(self, repository: Any) -> None:
        self.repository = repository

    def list_audit_logs(self, skip: int = 0, limit: int = 100) -> list[Any]:
        audit_logs: list[Any] = self.repository.list(skip=skip, limit=limit)
        return audit_logs

    def create_audit_log(self, payload: AuditLogCreate) -> Any:
        return self.repository.create(payload.model_dump())
