from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}


class TimestampedResponse(ORMModel):
    id: int
    created_at: datetime | str
    updated_at: datetime | str | None = None
