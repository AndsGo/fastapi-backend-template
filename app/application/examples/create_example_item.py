from typing import Any

from app.application.dto.example import CreateExampleItemCommand
from app.schemas.example import ExampleItemCreate
from app.services.example_service import ExampleItemService


class CreateExampleItemUseCase:
    def __init__(self, example_service: ExampleItemService) -> None:
        self.example_service = example_service

    def execute(self, command: CreateExampleItemCommand) -> Any:
        payload = ExampleItemCreate(**command.model_dump())
        return self.example_service.create_item(payload)
