import json
import typing
from datetime import timedelta

from redis.asyncio.client import Redis


async def cached_data(
    redis: Redis, data: typing.Any, key: str, ex: timedelta = timedelta(days=30)
):
    data: bytes = await redis.get(key)
    if not data:
        await redis.set(key, json.dumps(data), ex=ex)
    return data
