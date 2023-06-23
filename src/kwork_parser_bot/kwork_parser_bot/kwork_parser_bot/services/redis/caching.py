import json
import typing
from datetime import timedelta

from redis.asyncio.client import Redis


async def cached_data(
    redis: Redis,
    func: typing.Any = None,
    *,
    key: str,
    ex: timedelta = timedelta(days=1)
):
    cache_data: bytes = await redis.get(key)
    if not cache_data:
        data = await func()
        await redis.set(key, json.dumps(data.dict()), ex=ex)
        persist = await redis.persist(key)
        return data
    else:
        return json.loads(cache_data)
