import pytest
from sqlalchemy.engine import make_url

from app.db.engine import build_engine_options, validate_database_url


def test_postgresql_engine_options_are_explicit() -> None:
    url = make_url("postgresql+psycopg://app:secret@localhost/app")

    options = build_engine_options(url)

    assert options["pool_size"] == 20
    assert options["max_overflow"] == 30
    assert options["pool_pre_ping"] is True
    assert options["pool_recycle"] == 3600
    assert options["isolation_level"] == "READ COMMITTED"


def test_mysql_database_url_requires_utf8mb4_charset() -> None:
    url = make_url("mysql+pymysql://app:secret@localhost/app")

    with pytest.raises(ValueError, match="charset=utf8mb4"):
        validate_database_url(url)


def test_mysql_database_url_rejects_non_utf8mb4_charset() -> None:
    url = make_url("mysql+pymysql://app:secret@localhost/app?charset=utf8")

    with pytest.raises(ValueError, match="charset=utf8mb4"):
        validate_database_url(url)


def test_mysql_database_url_accepts_utf8mb4_charset() -> None:
    url = make_url("mysql+pymysql://app:secret@localhost/app?charset=utf8mb4")

    validated = validate_database_url(url)

    assert validated.query["charset"] == "utf8mb4"


def test_mysql_engine_options_are_explicit() -> None:
    url = make_url("mysql+pymysql://app:secret@localhost/app?charset=utf8mb4")

    options = build_engine_options(url)

    assert options["pool_size"] == 20
    assert options["max_overflow"] == 30
    assert options["pool_pre_ping"] is True
    assert options["pool_recycle"] == 3600
    assert options["isolation_level"] == "READ COMMITTED"
