from typing import Any

from app.services.example_service import ExampleItemService


class ListExampleItemsUseCase:
    def __init__(self, example_service: ExampleItemService) -> None:
        self.example_service = example_service

    def execute(self, *, skip: int = 0, limit: int = 100) -> list[Any]:
        return self.example_service.list_items(skip=skip, limit=limit)
