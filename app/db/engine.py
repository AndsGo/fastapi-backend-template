from typing import Any

from sqlalchemy.engine import URL, make_url

MYSQL_DIALECTS = {"mysql", "mysql+pymysql", "mysql+mysqldb", "mysql+mysqlclient"}


def validate_database_url(database_url: str | URL) -> URL:
    url = database_url if isinstance(database_url, URL) else make_url(database_url)
    if url.drivername in MYSQL_DIALECTS and url.query.get("charset") != "utf8mb4":
        raise ValueError(
            "MySQL DATABASE_URL must include charset=utf8mb4, for example "
            "mysql+pymysql://user:password@host:3306/db?charset=utf8mb4"
        )
    return url


def build_engine_options(database_url: str | URL) -> dict[str, Any]:
    validate_database_url(database_url)
    return {
        "pool_size": 20,
        "max_overflow": 30,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "isolation_level": "READ COMMITTED",
    }
