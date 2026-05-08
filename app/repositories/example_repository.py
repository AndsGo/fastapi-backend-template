from sqlalchemy import select

from app.models.example import ExampleItem
from app.repositories.base import SQLAlchemyRepository


class ExampleItemRepository(SQLAlchemyRepository[ExampleItem]):
    model = ExampleItem

    def get_by_code(self, code: str) -> ExampleItem | None:
        statement = select(ExampleItem).where(ExampleItem.code == code)
        return self.db.scalar(statement)
