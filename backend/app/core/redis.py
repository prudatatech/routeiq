"""Redis client configuration."""
import json
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.config import settings


redis_client = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def cache_get(key: str) -> Optional[Any]:
    """Get a cached value, auto-deserializing JSON."""
    value = await redis_client.get(key)
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


async def cache_set(key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL) -> None:
    """Set a cached value, auto-serializing to JSON."""
    serialized = json.dumps(value) if not isinstance(value, str) else value
    await redis_client.setex(key, ttl, serialized)


async def cache_delete(key: str) -> None:
    await redis_client.delete(key)


async def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching a pattern."""
    keys = await redis_client.keys(pattern)
    if keys:
        return await redis_client.delete(*keys)
    return 0
