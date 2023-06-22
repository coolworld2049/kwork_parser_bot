import json
from datetime import timedelta

from kwork import Kwork
from kwork.types import Category, Actor
from kwork.types.category import Subcategory
from redis.asyncio.client import Redis

from kwork_parser_bot.bots.dispatcher import redis
from kwork_parser_bot.bots.redis.caching import cached_data
from kwork_parser_bot.core.config import get_app_settings

kwork_api = Kwork(
    login=get_app_settings().KWORK_LOGIN,
    password=get_app_settings().KWORK_PASSWORD,
    phone_last=get_app_settings().KWORK_PHONE_LAST,
)


async def get_my_account(user_id: int):
    account: Actor = await cached_data(
        redis,
        kwork_api.get_me,
        key=f"kwork_api_me:{str(user_id)}",
        ex=timedelta(hours=1),
    )
    return account


async def cached_categories(
    redis: Redis, ex: timedelta = timedelta(days=30), *, kwork_api: Kwork = None
):
    # await redis.delete("kwork_api_categories")
    key = "kwork_api_categories"
    categories: list[Category] | bytes = await redis.get(key)
    if not categories:
        categories: list[Category] = await kwork_api.get_categories()
        await redis.set(key, json.dumps([x.json() for x in categories]), ex=ex)
        return categories
    else:
        persist = await redis.persist(key)
        categories = [Category(**json.loads(data)) for data in json.loads(categories)]
        return categories


def get_parent_category(categories: list[Category | Subcategory], category_id: int):
    item = list(filter(lambda x: x.id == category_id, categories))
    if item:
        item = item.pop()
    else:
        return None
    return item


def get_category(categories: list[Category], parent_category_id: int, category_id: int):
    parent_category = get_parent_category(categories, parent_category_id)
    category = get_parent_category(parent_category.subcategories, category_id)
    return category
