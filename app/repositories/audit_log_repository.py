from app.models.audit_log import AuditLog
from app.repositories.base import SQLAlchemyRepository


class AuditLogRepository(SQLAlchemyRepository[AuditLog]):
    model = AuditLog
