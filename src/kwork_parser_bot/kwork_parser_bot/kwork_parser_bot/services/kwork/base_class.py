import json
import typing
from datetime import timedelta
from typing import Any

from kwork import Kwork
from kwork.types import Actor, Category
from kwork.types.category import Subcategory
from pydantic import BaseModel
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from kwork_parser_bot.services.redis.main import cached_data


class KworkCreds(BaseModel):
    login: str
    password: str
    proxy: typing.Optional[str] = None
    phone_last: typing.Optional[str] = None


class KworkApi(Kwork):
    def __init__(self, kwork_creds: KworkCreds):
        super().__init__(**kwork_creds.dict(exclude_none=True))
        self.redis_prefix: str = "kwork_api"

    def kwork_creds_dict(self):
        return KworkCreds(**self.__dict__.copy()).dict(exclude_none=True)

    def _redis_key(self, value: Any):
        return f"{self.redis_prefix}:{str(value)}"

    async def get_my_account(self, user_id: int):
        account: Actor = await cached_data(
            self.get_me,
            key=self._redis_key(f"{__name__}:{user_id}"),
            ex=timedelta(hours=6),
        )
        return account

    async def cached_category(
        self,
        redis_pool: ConnectionPool,
        ex: timedelta = timedelta(days=30),
    ):
        # await redis.delete("kwork_api_categories")
        key = self._redis_key(__name__)
        async with Redis(connection_pool=redis_pool) as redis:
            categories: list[Category] | bytes = await redis.get(key)
            if not categories:
                categories: list[Category] = await self.get_categories()
                await redis.set(key, json.dumps([x.json() for x in categories]), ex=ex)
                return categories
            else:
                persist = await redis.persist(key)
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
