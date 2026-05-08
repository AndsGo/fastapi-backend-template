from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedResponse


class AuditLogCreate(BaseModel):
    actor_id: str = Field(min_length=1, max_length=128)
    actor_name: str = Field(min_length=1, max_length=128)
    action: str = Field(min_length=1, max_length=128)
    resource_type: str = Field(min_length=1, max_length=128)
    resource_id: str = Field(min_length=1, max_length=128)
    before_snapshot: dict[str, Any] | None = None
    after_snapshot: dict[str, Any] | None = None


class AuditLogResponse(TimestampedResponse):
    actor_id: str
    actor_name: str
    action: str
    resource_type: str
    resource_id: str
    before_snapshot: dict[str, Any] | None = None
    after_snapshot: dict[str, Any] | None = None
