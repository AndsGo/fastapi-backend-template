from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1.dependencies import (
    get_create_example_item_use_case,
    get_list_example_items_use_case,
)
from app.application.dto.example import CreateExampleItemCommand
from app.main import app


class FakeListExamplesUseCase:
    def execute(self, *, skip: int = 0, limit: int = 100) -> list[object]:
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


class FakeCreateExampleUseCase:
    def execute(self, command: CreateExampleItemCommand) -> object:
        return SimpleNamespace(
            id=2,
            code=command.code,
            name=command.name,
            description=command.description,
            created_at=datetime.now(UTC),
            updated_at=None,
        )


def override_list_examples_use_case() -> FakeListExamplesUseCase:
    return FakeListExamplesUseCase()


def override_create_example_use_case() -> FakeCreateExampleUseCase:
    return FakeCreateExampleUseCase()


def test_examples_path_is_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/v1/examples" in paths


def test_examples_list_endpoint_returns_items() -> None:
    app.dependency_overrides[get_list_example_items_use_case] = override_list_examples_use_case
    client = TestClient(app)
    try:
        response = client.get("/api/v1/examples")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()[0]["code"] == "sample"


def test_examples_create_endpoint_returns_item() -> None:
    app.dependency_overrides[get_create_example_item_use_case] = override_create_example_use_case
    client = TestClient(app)
    try:
        response = client.post(
            "/api/v1/examples",
            json={"code": "new-code", "name": "New Item"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["code"] == "new-code"
