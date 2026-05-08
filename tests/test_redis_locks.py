from typing import Any

import pytest

from app.jobs.locks import RedisDistributedLock


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}
        self.expire_calls = 0

    def set(self, key: str, value: str, *, nx: bool, ex: int) -> bool:
        if nx and key in self.values:
            return False

        self.values[key] = value
        self.ttls[key] = ex
        return True

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def expire(self, key: str, seconds: int) -> bool:
        self.expire_calls += 1
        if key not in self.values:
            return False

        self.ttls[key] = seconds
        return True

    def eval(self, script: str, numkeys: int, *keys_and_args: Any) -> int:
        assert numkeys == 1
        if "expire" in script:
            key, owner_token, ttl_seconds = keys_and_args
            if self.values.get(key) != owner_token:
                return 0

            self.ttls[key] = int(ttl_seconds)
            return 1

        key, owner_token = keys_and_args
        if self.values.get(key) != owner_token:
            return 0

        del self.values[key]
        self.ttls.pop(key, None)
        return 1


def test_lock_acquire_sets_owner_with_ttl() -> None:
    redis = FakeRedis()
    lock = RedisDistributedLock(redis, "scheduled-jobs", "worker-1", 30)

    acquired = lock.acquire()

    assert acquired is True
    assert redis.values["scheduled-jobs"] == "worker-1"
    assert redis.ttls["scheduled-jobs"] == 30


def test_lock_acquire_fails_when_another_owner_exists() -> None:
    redis = FakeRedis()
    first_lock = RedisDistributedLock(redis, "scheduled-jobs", "worker-1", 30)
    second_lock = RedisDistributedLock(redis, "scheduled-jobs", "worker-2", 30)

    assert first_lock.acquire() is True
    assert second_lock.acquire() is False
    assert redis.values["scheduled-jobs"] == "worker-1"


def test_lock_renew_requires_same_owner() -> None:
    redis = FakeRedis()
    original_owner = RedisDistributedLock(redis, "scheduled-jobs", "worker-1", 30)
    current_owner = RedisDistributedLock(redis, "scheduled-jobs", "worker-1", 60)
    different_owner = RedisDistributedLock(redis, "scheduled-jobs", "worker-2", 60)

    assert original_owner.acquire() is True
    assert different_owner.renew() is False
    assert redis.ttls["scheduled-jobs"] == 30
    assert current_owner.renew() is True
    assert redis.ttls["scheduled-jobs"] == 60
    assert redis.expire_calls == 0


def test_lock_release_deletes_only_same_owner() -> None:
    redis = FakeRedis()
    current_owner = RedisDistributedLock(redis, "scheduled-jobs", "worker-1", 30)
    different_owner = RedisDistributedLock(redis, "scheduled-jobs", "worker-2", 30)

    assert current_owner.acquire() is True
    assert different_owner.release() is False
    assert redis.values["scheduled-jobs"] == "worker-1"
    assert current_owner.release() is True
    assert redis.get("scheduled-jobs") is None


def test_lock_requires_positive_ttl() -> None:
    redis = FakeRedis()

    with pytest.raises(ValueError, match="ttl_seconds must be greater than 0"):
        RedisDistributedLock(redis, "scheduled-jobs", "worker-1", 0)
