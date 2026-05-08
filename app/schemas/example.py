from pydantic import BaseModel, Field

from app.schemas.common import TimestampedResponse


class ExampleItemCreate(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None


class ExampleItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None


class ExampleItemResponse(TimestampedResponse):
    code: str
    name: str
    description: str | None = None
