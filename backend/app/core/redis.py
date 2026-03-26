"""Redis client configuration."""
import json
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.config import settings


# Redis Client Initialization
# We support standard redis (aioredis) OR Upstash Redis (HTTP)
try:
    if settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN:
        from upstash_redis import Redis as UpstashRedis
        # We wrap Upstash to provide an async-like interface or use it directly
        # For simplicity, we'll use a wrapper or the standard client if possible
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    else:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
except Exception:
    redis_client = None


async def cache_get(key: str) -> Optional[Any]:
    if not redis_client:
        return None
    try:
        value = await redis_client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except Exception:
        return None


async def cache_set(key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL) -> None:
    if not redis_client:
        return
    try:
        serialized = json.dumps(value) if not isinstance(value, str) else value
        await redis_client.setex(key, ttl, serialized)
    except Exception:
        pass


async def cache_delete(key: str) -> None:
    await redis_client.delete(key)


async def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching a pattern."""
    keys = await redis_client.keys(pattern)
    if keys:
        return await redis_client.delete(*keys)
    return 0
