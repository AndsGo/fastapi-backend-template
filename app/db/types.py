from sqlalchemy import String
from sqlalchemy.dialects import mysql
from sqlalchemy.sql.type_api import TypeEngine


def case_sensitive_string(length: int) -> TypeEngine[str]:
    return String(length).with_variant(
        mysql.VARCHAR(length=length, collation="utf8mb4_bin"),
        "mysql",
    )
