import json
import typing
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Any, AsyncGenerator

from loguru import logger
from redis.asyncio import ConnectionPool
from redis.asyncio.client import Redis

from kwork_api.api.kwork import Kwork
from kwork_api.api.types import Category, Project
from kwork_api.api.types.category import Subcategory


class KworkApi(Kwork):
    def __init__(
        self,
        login: str,
        password: str,
        proxy: typing.Optional[str] = None,
        phone: typing.Optional[str] = None,
        token: typing.Optional[str] = None,
        *args,
        **kwargs,
    ):
        super().__init__(
            login=login,
            password=password,
            proxy=proxy,
            phone=phone,
        )
        self._token = token
        self.redis_prefix = KworkApi.__class__.__name__

    def _r_key(self, value: Any):
        return f"{self.redis_prefix}:{str(value)}"

    async def cached_category(
        self,
        redis_pool,
        ex: timedelta = timedelta(days=30),
    ):
        key = self._r_key("category")
        async with Redis(connection_pool=redis_pool) as redis:
            await redis.expire(key, ex)
            data = await redis.get(key)
            if not data:
                data = await self.get_categories()
                await redis.set(key, json.dumps([x.json() for x in data]), ex=ex)
                return data
            else:
                data = [Category(**json.loads(x)) for x in json.loads(data)]
                return data

    async def cached_projects(
        self,
        redis_pool: ConnectionPool,
        categories_ids: list[int],
        data: list[Project] = None,
        ex: int = 86400,
        update=False,
    ):
        key = self._r_key(f"projects:{':'.join([str(x) for x in categories_ids])}")
        async with Redis(connection_pool=redis_pool) as redis:
            await redis.expire(key, ex)
            if data:
                data_json = json.dumps([x.json() for x in data])
                if update:
                    await redis.set(key, data_json, ex=ex)
            cached_data = await redis.get(key)
            if not cached_data and data:
                await redis.set(key, data_json, ex=ex)
                return data
            elif cached_data and not data:
                return [Project(**json.loads(x)) for x in json.loads(cached_data)]
            else:
                return data

    @staticmethod
    def get_parent_category(category: list[Category | Subcategory], category_id: int):
        item = list(filter(lambda x: x.id == category_id, category))
        if item:
            item = item.pop()
        else:
            return None
        return item

    def get_category(
        self, category: list[Category], parent_category_id: int, category_id: int
    ):
        parent_category = self.get_parent_category(category, parent_category_id)
        category = self.get_parent_category(parent_category.subcategories, category_id)
        return category


@asynccontextmanager
async def get_kwork_api(
    *args,
    **kwargs,
) -> AsyncGenerator[KworkApi, None]:
    kwork_api = KworkApi(*args, **kwargs)
    try:
        yield kwork_api
    except Exception as e:
        logger.debug(e)
        raise e
    finally:
        await kwork_api.close()
