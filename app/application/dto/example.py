from pydantic import BaseModel, Field


class CreateExampleItemCommand(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None


class UpdateExampleItemCommand(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
