from sqlalchemy.dialects import mysql, postgresql

from app.db.types import case_sensitive_string
from app.models.example import ExampleItem
from app.models.scheduled_job import ScheduledJob


def test_case_sensitive_string_uses_mysql_binary_collation() -> None:
    column_type = case_sensitive_string(64)
    mysql_type = column_type.dialect_impl(mysql.dialect())

    assert getattr(mysql_type, "collation", None) == "utf8mb4_bin"


def test_case_sensitive_string_does_not_leak_mysql_collation_to_postgresql() -> None:
    column_type = case_sensitive_string(64)
    compiled = column_type.compile(dialect=postgresql.dialect())

    assert "utf8mb4_bin" not in compiled


def test_unique_business_key_columns_use_mysql_binary_collation() -> None:
    dialect = mysql.dialect()
    columns = [
        ExampleItem.__table__.c.code,
        ScheduledJob.__table__.c.code,
    ]

    for column in columns:
        assert getattr(column.type.dialect_impl(dialect), "collation", None) == "utf8mb4_bin"
