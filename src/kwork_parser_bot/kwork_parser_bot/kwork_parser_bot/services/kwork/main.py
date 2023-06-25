import json
from datetime import timedelta
from typing import Any

from pydantic import BaseModel
from redis.asyncio.client import Redis

from kwork_parser_bot.services.kwork.kwork import Kwork
from kwork_parser_bot.services.kwork.kwork.types import Actor, Category, Project
from kwork_parser_bot.services.kwork.kwork.types.category import Subcategory
from kwork_parser_bot.services.redis.lifetime import redis_pool
from kwork_parser_bot.services.redis.main import cached_data, delete_data, retrieve_data


class KworkCreds(BaseModel):
    login: str
    password: str
    phone: str | None = None

    @property
    def phone_last(self):
        if self.phone:
            return self.phone[-4:]

    @classmethod
    async def set_cache(
        cls, user_id, data: dict, ex: int | timedelta = timedelta(days=7)
    ):
        kwork_creds = await cached_data(
            data=data, key=f"kwork_api:creds:{user_id}", ex=ex, update=True
        )
        if kwork_creds:
            return KworkCreds(**kwork_creds)
        else:
            return None

    @classmethod
    async def delete_cache(
        cls,
        user_id,
    ):
        return await delete_data([f"kwork_api:creds:{user_id}"])

    @staticmethod
    async def get_cached(user_id):
        kwork_creds = await retrieve_data(key=f"kwork_api:creds:{user_id}")
        if kwork_creds:
            return KworkCreds(**kwork_creds)
        else:
            return None


class KworkApi(Kwork):
    def __init__(self, creds: KworkCreds):
        super().__init__(
            login=creds.login,
            password=creds.password,
            phone_last=creds.phone_last,
        )
        self.creds = creds
        self.redis_prefix: str = "kwork_api"

    def _build_redis_key(self, value: Any):
        return f"{self.redis_prefix}:{str(value)}"

    async def my_account(self, user_id: int):
        account: Actor = await cached_data(
            self.get_me,
            key=self._build_redis_key(f"{self.my_account.__name__}:{user_id}"),
            ex=timedelta(hours=6),
        )
        return account

    async def cached_category(
        self,
        ex: timedelta = timedelta(days=30),
    ):
        key = self._build_redis_key(self.cached_category.__name__)
        async with Redis(connection_pool=redis_pool) as redis:
            await redis.expire(key, ex)
            data: list[Category] | bytes = await redis.get(key)
            if not data:
                data = await self.get_categories()
                await redis.set(key, json.dumps([x.json() for x in data]), ex=ex)
                return data
            else:
                data = [Category(**json.loads(x)) for x in json.loads(data)]
                return data

    async def cached_projects(
        self,
        user_id: int,
        categories_ids: list[int],
        data: list[Project] = None,
        ex: timedelta = timedelta(days=1),
        update=False,
    ):
        key = self._build_redis_key(
            f"{self.cached_projects.__name__}:"
            f"{'-'.join([str(x) for x in categories_ids])}"
        )
        async with Redis(connection_pool=redis_pool) as redis:
            await redis.expire(key, ex)
            if update:
                await redis.set(key, json.dumps([x.json() for x in data]), ex=ex)
            cached_data: list[Project] | bytes = await redis.get(key)
            if not cached_data and data:
                await redis.set(key, json.dumps([x.json() for x in data]), ex=ex)
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
