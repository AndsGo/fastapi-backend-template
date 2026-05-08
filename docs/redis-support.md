# Redis Support

Redis is optional shared infrastructure. It is used by the job system for distributed locks and can be used by application modules for cache, idempotency, rate limits, or heartbeats.

## Files

```text
app/cache/redis.py
app/cache/keys.py
```

## Key Rules

- Define reusable key templates in `RedisKey`.
- Build keys with `build_cache_key()`.
- Use `REDIS_PREFIX` to isolate environments or applications.
- Do not concatenate Redis keys throughout business code.

Example:

```python
from app.cache.keys import RedisKey, build_cache_key

key = build_cache_key(RedisKey.EXAMPLE_ITEM, item_id=1)
```

## Configuration

```dotenv
REDIS_URL=redis://localhost:6379/0
REDIS_PREFIX=backend
REDIS_DEFAULT_TTL_SECONDS=300
```
