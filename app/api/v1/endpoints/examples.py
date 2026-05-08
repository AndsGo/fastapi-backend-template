from typing import Any

from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import (
    get_create_example_item_use_case,
    get_get_example_item_use_case,
    get_list_example_items_use_case,
    get_update_example_item_use_case,
)
from app.application.dto.example import CreateExampleItemCommand, UpdateExampleItemCommand
from app.application.examples.create_example_item import CreateExampleItemUseCase
from app.application.examples.get_example_item import GetExampleItemUseCase
from app.application.examples.list_example_items import ListExampleItemsUseCase
from app.application.examples.update_example_item import UpdateExampleItemUseCase
from app.schemas.example import ExampleItemCreate, ExampleItemResponse, ExampleItemUpdate

router = APIRouter()


@router.get("", response_model=list[ExampleItemResponse])
def list_examples(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    use_case: ListExampleItemsUseCase = Depends(get_list_example_items_use_case),
) -> list[Any]:
    return use_case.execute(skip=skip, limit=limit)


@router.post("", response_model=ExampleItemResponse, status_code=201)
def create_example(
    payload: ExampleItemCreate,
    use_case: CreateExampleItemUseCase = Depends(get_create_example_item_use_case),
) -> Any:
    return use_case.execute(CreateExampleItemCommand(**payload.model_dump()))


@router.get("/{item_id}", response_model=ExampleItemResponse)
def get_example(
    item_id: int,
    use_case: GetExampleItemUseCase = Depends(get_get_example_item_use_case),
) -> Any:
    return use_case.execute(item_id)


@router.patch("/{item_id}", response_model=ExampleItemResponse)
def update_example(
    item_id: int,
    payload: ExampleItemUpdate,
    use_case: UpdateExampleItemUseCase = Depends(get_update_example_item_use_case),
) -> Any:
    return use_case.execute(
        item_id,
        UpdateExampleItemCommand(**payload.model_dump(exclude_unset=True)),
    )
