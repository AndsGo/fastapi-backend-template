import pytest

from app.cache.keys import RedisKey, build_cache_key


def test_build_cache_key_adds_prefix_and_normalizes_parts() -> None:
    assert build_cache_key("example", " item ", 1001, prefix="tpl") == "tpl:example:item:1001"


def test_build_cache_key_skips_empty_parts() -> None:
    assert build_cache_key("example", "", None, "status", prefix="tpl") == "tpl:example:status"


def test_build_cache_key_renders_redis_key_template() -> None:
    assert (
        build_cache_key(RedisKey.EXAMPLE_ITEM, item_id=1001, prefix="tpl")
        == "tpl:example:item:1001"
    )


def test_build_cache_key_requires_template_variables() -> None:
    with pytest.raises(ValueError, match="item_id"):
        build_cache_key(RedisKey.EXAMPLE_ITEM, prefix="tpl")


def test_build_cache_key_renders_idempotency_key() -> None:
    assert build_cache_key(
        RedisKey.OPERATION_IDEMPOTENCY,
        operation_type="create",
        business_key="example-1",
        prefix="tpl",
    ) == "tpl:idempotency:create:example-1"


def test_build_cache_key_renders_scheduled_job_lock() -> None:
    assert build_cache_key(RedisKey.SCHEDULED_JOB_LOCK, job_id=42, prefix="pls") == (
        "pls:scheduler:job:42:lock"
    )


def test_build_cache_key_renders_scheduled_run_lock() -> None:
    assert build_cache_key(RedisKey.SCHEDULED_RUN_LOCK, run_id=91, prefix="pls") == (
        "pls:scheduler:run:91:lock"
    )


def test_build_cache_key_renders_rate_limit_key() -> None:
    assert build_cache_key(
        RedisKey.RATE_LIMIT,
        scope="user",
        scope_id="42",
        prefix="pls",
    ) == "pls:rate_limit:user:42"


def test_build_cache_key_renders_worker_heartbeat() -> None:
    assert build_cache_key(RedisKey.WORKER_HEARTBEAT, worker_id="worker-1", prefix="pls") == (
        "pls:heartbeat:worker:worker-1"
    )
