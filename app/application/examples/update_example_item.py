from typing import Any

from app.application.dto.example import UpdateExampleItemCommand
from app.schemas.example import ExampleItemUpdate
from app.services.example_service import ExampleItemService


class UpdateExampleItemUseCase:
    def __init__(self, example_service: ExampleItemService) -> None:
        self.example_service = example_service

    def execute(self, item_id: int, command: UpdateExampleItemCommand) -> Any:
        payload = ExampleItemUpdate(**command.model_dump(exclude_unset=True))
        return self.example_service.update_item(item_id, payload)
