from typing import Any

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.example_repository import ExampleItemRepository
from app.schemas.example import ExampleItemCreate, ExampleItemUpdate


class ExampleItemService:
    def __init__(self, repository: ExampleItemRepository) -> None:
        self.repository = repository

    def list_items(self, skip: int = 0, limit: int = 100) -> list[Any]:
        items: list[Any] = self.repository.list(skip=skip, limit=limit)
        return items

    def get_item(self, item_id: int) -> Any:
        item = self.repository.get(item_id)
        if item is None:
            raise NotFoundError("example_item", item_id)
        return item

    def create_item(self, payload: ExampleItemCreate) -> Any:
        if self.repository.get_by_code(payload.code) is not None:
            raise ConflictError("example_item", "code already exists")
        return self.repository.create(payload.model_dump())

    def update_item(self, item_id: int, payload: ExampleItemUpdate) -> Any:
        item = self.get_item(item_id)
        return self.repository.update(item, payload.model_dump(exclude_unset=True))
