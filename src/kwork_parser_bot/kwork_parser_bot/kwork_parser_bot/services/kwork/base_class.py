import json
from datetime import timedelta
from typing import Any

from kwork import Kwork
from kwork.types import Actor, Category
from kwork.types.category import Subcategory
from pydantic import BaseModel
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from kwork_parser_bot.services.redis.main import cached_data, delete_data, retrieve_data


class KworkCreds(BaseModel):
    login: str
    password: str
    phone: str | None = None

    @property
    def phone_last(self):
        return self.phone[-4:]

    @classmethod
    async def set_cache(
        cls, user_id, data: dict, ex: int | timedelta = timedelta(days=7)
    ):
        return await cached_data(
            data=data, key=f"kwork_api:creds:{user_id}", ex=ex, update=True
        )

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
            return kwork_creds


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
        redis_pool: ConnectionPool,
        ex: timedelta = timedelta(days=30),
    ):
        key = self._build_redis_key(self.cached_category.__name__)
        async with Redis(connection_pool=redis_pool) as redis:
            categories: list[Category] | bytes = await redis.get(key)
            if not categories:
                categories: list[Category] = await self.get_categories()
                await redis.set(key, json.dumps([x.json() for x in categories]), ex=ex)
                return categories
            else:
                categories = [
                    Category(**json.loads(data)) for data in json.loads(categories)
                ]
                return categories

    @staticmethod
    def get_parent_category(categories: list[Category | Subcategory], category_id: int):
        item = list(filter(lambda x: x.id == category_id, categories))
        if item:
            item = item.pop()
        else:
            return None
        return item

    def get_category(
        self, categories: list[Category], parent_category_id: int, category_id: int
    ):
        parent_category = self.get_parent_category(categories, parent_category_id)
        category = self.get_parent_category(parent_category.subcategories, category_id)
        return category
