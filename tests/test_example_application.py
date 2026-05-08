from datetime import UTC, datetime
from types import SimpleNamespace

from app.application.dto.example import CreateExampleItemCommand, UpdateExampleItemCommand
from app.application.examples.create_example_item import CreateExampleItemUseCase
from app.application.examples.get_example_item import GetExampleItemUseCase
from app.application.examples.list_example_items import ListExampleItemsUseCase
from app.application.examples.update_example_item import UpdateExampleItemUseCase
from app.schemas.example import ExampleItemCreate, ExampleItemUpdate


class FakeExampleService:
    def __init__(self) -> None:
        self.created_payload: ExampleItemCreate | None = None
        self.updated_payload: ExampleItemUpdate | None = None

    def list_items(self, skip: int = 0, limit: int = 100) -> list[object]:
        return [
            SimpleNamespace(
                id=1,
                code="sample",
                name="Sample",
                description=None,
                created_at=datetime.now(UTC),
                updated_at=None,
            )
        ][skip : skip + limit]

    def get_item(self, item_id: int) -> object:
        return SimpleNamespace(
            id=item_id,
            code="sample",
            name="Sample",
            description=None,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

    def create_item(self, payload: ExampleItemCreate) -> object:
        self.created_payload = payload
        return SimpleNamespace(
            id=2,
            code=payload.code,
            name=payload.name,
            description=payload.description,
            created_at=datetime.now(UTC),
            updated_at=None,
        )

    def update_item(self, item_id: int, payload: ExampleItemUpdate) -> object:
        self.updated_payload = payload
        return SimpleNamespace(
            id=item_id,
            code="sample",
            name=payload.name or "Sample",
            description=payload.description,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )


def test_create_example_item_use_case_maps_command_to_service_payload() -> None:
    service = FakeExampleService()

    item = CreateExampleItemUseCase(service).execute(
        CreateExampleItemCommand(code="new-code", name="New Item"),
    )

    assert service.created_payload == ExampleItemCreate(code="new-code", name="New Item")
    assert item.code == "new-code"


def test_list_example_items_use_case_delegates_to_service() -> None:
    items = ListExampleItemsUseCase(FakeExampleService()).execute(skip=0, limit=10)

    assert len(items) == 1


def test_get_example_item_use_case_delegates_to_service() -> None:
    item = GetExampleItemUseCase(FakeExampleService()).execute(1)

    assert item.id == 1


def test_update_example_item_use_case_maps_command_to_service_payload() -> None:
    service = FakeExampleService()

    item = UpdateExampleItemUseCase(service).execute(
        1,
        UpdateExampleItemCommand(name="Renamed"),
    )

    assert service.updated_payload == ExampleItemUpdate(name="Renamed")
    assert item.name == "Renamed"
