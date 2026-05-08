from typing import Any

from app.services.example_service import ExampleItemService


class GetExampleItemUseCase:
    def __init__(self, example_service: ExampleItemService) -> None:
        self.example_service = example_service

    def execute(self, item_id: int) -> Any:
        return self.example_service.get_item(item_id)
