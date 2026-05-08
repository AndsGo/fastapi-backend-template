from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from app.core.exceptions import ConflictError, NotFoundError
from app.schemas.example import ExampleItemCreate, ExampleItemUpdate
from app.services.example_service import ExampleItemService


class FakeExampleRepository:
    def __init__(self) -> None:
        self.items = {
            1: SimpleNamespace(
                id=1,
                code="sample",
                name="Sample",
                description=None,
                created_at=datetime.now(UTC),
                updated_at=None,
            )
        }

    def list(self, skip: int = 0, limit: int = 100) -> list[object]:
        return list(self.items.values())[skip : skip + limit]

    def get(self, resource_id: int) -> object | None:
        return self.items.get(resource_id)

    def get_by_code(self, code: str) -> object | None:
        return next((item for item in self.items.values() if item.code == code), None)

    def create(self, payload: dict[str, object]) -> object:
        item = SimpleNamespace(
            id=2,
            created_at=datetime.now(UTC),
            updated_at=None,
            **payload,
        )
        self.items[item.id] = item
        return item

    def update(self, entity: object, payload: dict[str, object]) -> object:
        for key, value in payload.items():
            setattr(entity, key, value)
        entity.updated_at = datetime.now(UTC)
        return entity


def test_example_service_creates_item() -> None:
    service = ExampleItemService(FakeExampleRepository())

    item = service.create_item(
        ExampleItemCreate(code="new-code", name="New Item", description="Example"),
    )

    assert item.code == "new-code"
    assert item.name == "New Item"


def test_example_service_rejects_duplicate_code() -> None:
    service = ExampleItemService(FakeExampleRepository())

    with pytest.raises(ConflictError):
        service.create_item(ExampleItemCreate(code="sample", name="Duplicate"))


def test_example_service_raises_not_found() -> None:
    service = ExampleItemService(FakeExampleRepository())

    with pytest.raises(NotFoundError):
        service.get_item(999)


def test_example_service_updates_item() -> None:
    service = ExampleItemService(FakeExampleRepository())

    item = service.update_item(1, ExampleItemUpdate(name="Renamed"))

    assert item.name == "Renamed"
