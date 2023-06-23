import json
import typing
from datetime import timedelta

from redis.asyncio import Redis

from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.services.redis.lifetime import redis_pool

redis = Redis(
    host=get_app_settings().REDIS_MASTER_HOST,
    port=get_app_settings().REDIS_MASTER_PORT_NUMBER,
    password=get_app_settings().REDIS_PASSWORD,
    db=get_app_settings().REDIS_DATABASE,
    max_connections=get_app_settings().REDIS_MAX_CONNECTIONS,
)


async def cached_data(
    func: typing.Any = None,
    *,
    key: str,
    ex: timedelta = timedelta(days=1)
):
    async with Redis(connection_pool=redis_pool) as redis:
        cache_data: bytes = await redis.get(key)
        if not cache_data:
            data = await func()
            await redis.set(key, json.dumps(data.dict()), ex=ex)
            persist = await redis.persist(key)
            return data
        else:
            return json.loads(cache_data)
