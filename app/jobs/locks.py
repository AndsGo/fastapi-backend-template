from typing import Protocol

RELEASE_LOCK_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
end
return 0
"""

RENEW_LOCK_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("expire", KEYS[1], ARGV[2])
end
return 0
"""


class RedisLockClient(Protocol):
    def set(self, key: str, value: str, *, nx: bool, ex: int) -> bool: ...

    def eval(self, script: str, numkeys: int, *keys_and_args: str) -> int: ...


class RedisDistributedLock:
    def __init__(
        self,
        redis_client: RedisLockClient,
        key: str,
        owner_token: str,
        ttl_seconds: int,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than 0")

        self._redis_client = redis_client
        self._key = key
        self._owner_token = owner_token
        self._ttl_seconds = ttl_seconds

    def acquire(self) -> bool:
        return bool(
            self._redis_client.set(
                self._key,
                self._owner_token,
                nx=True,
                ex=self._ttl_seconds,
            )
        )

    def renew(self) -> bool:
        renewed_count = self._redis_client.eval(
            RENEW_LOCK_SCRIPT,
            1,
            self._key,
            self._owner_token,
            str(self._ttl_seconds),
        )
        return renewed_count == 1

    def release(self) -> bool:
        deleted_count = self._redis_client.eval(
            RELEASE_LOCK_SCRIPT,
            1,
            self._key,
            self._owner_token,
        )
        return deleted_count == 1
