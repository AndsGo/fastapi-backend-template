from fastapi import APIRouter, Depends, Query

from app.application.audit_logs.list_audit_logs import ListAuditLogsUseCase
from app.application.providers import get_list_audit_logs_use_case
from app.schemas.audit_log import AuditLogResponse

router = APIRouter()


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    use_case: ListAuditLogsUseCase = Depends(get_list_audit_logs_use_case),
) -> list[AuditLogResponse]:
    return use_case.execute(skip=skip, limit=limit)
