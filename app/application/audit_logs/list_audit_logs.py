from typing import Any

from app.services.audit_log_service import AuditLogService


class ListAuditLogsUseCase:
    def __init__(self, service: AuditLogService) -> None:
        self.service = service

    def execute(self, *, skip: int = 0, limit: int = 100) -> list[Any]:
        audit_logs: list[Any] = self.service.list_audit_logs(skip=skip, limit=limit)
        return audit_logs
