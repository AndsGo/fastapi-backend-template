from enum import StrEnum
from string import Formatter
from typing import Any

from app.core.config import settings


class RedisKey(StrEnum):
    EXAMPLE_ITEM = "example:item:{item_id}"
    SCHEDULED_JOB_LOCK = "scheduler:job:{job_id}:lock"
    SCHEDULED_RUN_LOCK = "scheduler:run:{run_id}:lock"
    OPERATION_IDEMPOTENCY = "idempotency:{operation_type}:{business_key}"
    RATE_LIMIT = "rate_limit:{scope}:{scope_id}"
    WORKER_HEARTBEAT = "heartbeat:worker:{worker_id}"
    SCHEDULER_HEARTBEAT = "heartbeat:scheduler:{scheduler_id}"


def build_cache_key(*parts: Any, prefix: str | None = None, **template_values: Any) -> str:
    if len(parts) == 1 and isinstance(parts[0], RedisKey):
        rendered_key = _render_template(parts[0], template_values)
        return _join_key_parts([rendered_key], prefix=prefix)
    if template_values:
        raise ValueError("Template values are only supported when the first argument is RedisKey.")
    return _join_key_parts(parts, prefix=prefix)


def _render_template(redis_key: RedisKey, values: dict[str, Any]) -> str:
    required_fields = {
        field_name
        for _, field_name, _, _ in Formatter().parse(redis_key.value)
        if field_name is not None
    }
    missing_fields = sorted(field for field in required_fields if field not in values)
    if missing_fields:
        raise ValueError(f"Missing Redis key template values: {', '.join(missing_fields)}")
    return redis_key.value.format(**values)


def _join_key_parts(parts: Any, prefix: str | None = None) -> str:
    normalized_parts = [
        str(part).strip().replace(" ", "_")
        for part in parts
        if part is not None and str(part).strip()
    ]
    key_prefix = (prefix or settings.redis_prefix).strip()
    return ":".join([key_prefix, *normalized_parts])
