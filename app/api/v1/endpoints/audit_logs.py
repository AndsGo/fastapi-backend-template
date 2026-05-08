from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import get_audit_log_service
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_log_service import AuditLogService

router = APIRouter()


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: AuditLogService = Depends(get_audit_log_service),
) -> list[AuditLogResponse]:
    return service.list_audit_logs(skip=skip, limit=limit)
