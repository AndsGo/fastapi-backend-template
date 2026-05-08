from redis import Redis

from app.core.config import Settings, settings

_redis_client: Redis | None = None


def get_redis_client(config: Settings | None = None) -> Redis:
    global _redis_client
    if _redis_client is None:
        selected_settings = config or settings
        _redis_client = Redis.from_url(
            selected_settings.redis_url,
            decode_responses=True,
        )
    return _redis_client


def close_redis_client() -> None:
    global _redis_client
    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
