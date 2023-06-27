import asyncio
import json

import pytest
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool


@pytest.mark.asyncio
async def test_redis_pool(event_loop, fake_redis_pool: ConnectionPool):
    async with Redis(connection_pool=fake_redis_pool) as redis:
        key = "test_redis_pool"
        data = {"test": "test"}
        await redis.set(key, json.dumps(data), ex=3)
        cached_data = await redis.get(key)
        assert json.loads(cached_data) and data == json.loads(cached_data)
        await asyncio.sleep(3.2)
        cached_data = await redis.get(key)
        assert not cached_data
