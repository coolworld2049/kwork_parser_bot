import asyncio
import json
import typing
from datetime import timedelta

from loguru import logger
from redis.asyncio import Redis

from kwork_parser_bot.services.redis.lifetime import redis_pool


async def cached_data(
    func: typing.Any = None,
    data: dict = None,
    *,
    key: str = None,
    ex: int | timedelta = timedelta(days=1),
    update=False
):
    try:
        async with Redis(connection_pool=redis_pool) as redis:
            await redis.expire(key, ex)
            if update:
                await redis.set(key, json.dumps(data), ex=ex)
                return data
            cache_data: bytes = await redis.get(key)
            if not cache_data or cache_data == b"null":
                if func:
                    if asyncio.iscoroutinefunction(func):
                        data = await func()
                    else:
                        data = func()
                    data = data.dict() if not isinstance(data, dict) else None
                await redis.set(key, json.dumps(data), ex=ex)
                return data
            else:
                return json.loads(cache_data)
    except Exception as e:
        logger.debug(e.args)


async def retrieve_data(key: str):
    async with Redis(connection_pool=redis_pool) as redis:
        data = await redis.get(key)
        return json.loads(data) if data else data


async def delete_data(keys: list | tuple):
    async with Redis(connection_pool=redis_pool) as redis:
        return await redis.delete(*keys)
