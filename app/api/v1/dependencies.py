from collections.abc import Callable
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.application.examples.create_example_item import CreateExampleItemUseCase
from app.application.examples.get_example_item import GetExampleItemUseCase
from app.application.examples.list_example_items import ListExampleItemsUseCase
from app.application.examples.update_example_item import UpdateExampleItemUseCase
from app.db.session import get_db
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.example_repository import ExampleItemRepository
from app.repositories.scheduled_job_repository import (
    ScheduledJobRepository,
    ScheduledJobRunRepository,
)
from app.services.audit_log_service import AuditLogService
from app.services.example_service import ExampleItemService
from app.services.scheduled_job_service import ScheduledJobService


@dataclass(frozen=True)
class UserContext:
    actor_id: str
    actor_name: str
    permissions: tuple[str, ...] = ()


def get_current_user(
    x_actor_id: str | None = Header(default=None),
    x_actor_name: str | None = Header(default=None),
) -> UserContext:
    return UserContext(
        actor_id=x_actor_id or "system",
        actor_name=x_actor_name or "System",
        permissions=(),
    )


def require_permission(permission: str) -> Callable[[UserContext], UserContext]:
    def dependency(current_user: UserContext = Depends(get_current_user)) -> UserContext:
        if permission and permission not in current_user.permissions:
            # Placeholder behavior: do not enforce permissions until auth is implemented.
            return current_user
        return current_user

    return dependency


def get_example_item_service(db: Session = Depends(get_db)) -> ExampleItemService:
    return ExampleItemService(ExampleItemRepository(db))


def get_list_example_items_use_case(
    service: ExampleItemService = Depends(get_example_item_service),
) -> ListExampleItemsUseCase:
    return ListExampleItemsUseCase(service)


def get_create_example_item_use_case(
    service: ExampleItemService = Depends(get_example_item_service),
) -> CreateExampleItemUseCase:
    return CreateExampleItemUseCase(service)


def get_get_example_item_use_case(
    service: ExampleItemService = Depends(get_example_item_service),
) -> GetExampleItemUseCase:
    return GetExampleItemUseCase(service)


def get_update_example_item_use_case(
    service: ExampleItemService = Depends(get_example_item_service),
) -> UpdateExampleItemUseCase:
    return UpdateExampleItemUseCase(service)


def get_audit_log_service(db: Session = Depends(get_db)) -> AuditLogService:
    return AuditLogService(AuditLogRepository(db))


def get_scheduled_job_service(db: Session = Depends(get_db)) -> ScheduledJobService:
    return ScheduledJobService(ScheduledJobRepository(db), ScheduledJobRunRepository(db))


def unsupported_auth_flow() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication flow is reserved for SSO/OAuth2 or RBAC integration.",
    )
