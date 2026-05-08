from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class SQLAlchemyRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, skip: int = 0, limit: int = 100) -> list[ModelT]:
        statement = select(self.model).offset(skip).limit(limit)
        return list(self.db.scalars(statement).all())

    def get(self, resource_id: int) -> ModelT | None:
        return self.db.get(self.model, resource_id)

    def create(self, payload: dict[str, Any]) -> ModelT:
        entity = self.model(**payload)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: ModelT, payload: dict[str, Any]) -> ModelT:
        for field, value in payload.items():
            setattr(entity, field, value)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
