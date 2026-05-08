from app.cache.redis import close_redis_client, get_redis_client
from app.core.config import Settings


def test_get_redis_client_reuses_lazy_client_instance() -> None:
    settings = Settings(redis_url="redis://localhost:6379/9")

    first = get_redis_client(settings)
    second = get_redis_client(settings)

    assert first is second
    close_redis_client()


def test_get_redis_client_does_not_connect_during_creation() -> None:
    settings = Settings(redis_url="redis://localhost:6379/9")

    client = get_redis_client(settings)

    assert client.connection_pool.connection_kwargs["db"] == 9
    close_redis_client()
