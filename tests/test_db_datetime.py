from collections.abc import Callable
from datetime import UTC, datetime

from app.models.example import ExampleItem


def test_timestamp_defaults_are_timezone_aware_utc() -> None:
    default_factory = ExampleItem.__table__.c.created_at.default.arg
    assert isinstance(default_factory, Callable)

    value = default_factory(None)

    assert isinstance(value, datetime)
    assert value.tzinfo is UTC
    assert value.utcoffset().total_seconds() == 0


def test_timestamp_update_defaults_are_timezone_aware_utc() -> None:
    update_factory = ExampleItem.__table__.c.updated_at.onupdate.arg
    assert isinstance(update_factory, Callable)

    value = update_factory(None)

    assert isinstance(value, datetime)
    assert value.tzinfo is UTC
    assert value.utcoffset().total_seconds() == 0
