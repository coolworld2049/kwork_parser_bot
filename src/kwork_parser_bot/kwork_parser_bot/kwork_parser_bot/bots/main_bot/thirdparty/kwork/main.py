import json
from datetime import timedelta

from kwork import Kwork
from kwork.types import Category, Project
from redis.asyncio.client import Redis

from kwork_parser_bot.core.config import get_app_settings

kwork_api = Kwork(
    login=get_app_settings().KWORK_LOGIN,
    password=get_app_settings().KWORK_PASSWORD,
    phone_last=get_app_settings().KWORK_PHONE_LAST,
)


async def cached_categories(redis: Redis, ex: timedelta = timedelta(days=1)):
    # await redis.delete("kwork_api_categories")
    categories: list[Category] | bytes = await redis.get("kwork_api_categories")
    if not categories:
        categories: list[Category] = await kwork_api.get_categories()
        await redis.set(
            "kwork_api_categories", json.dumps([x.json() for x in categories]), ex=ex
        )
    categories = [Category(**json.loads(data)) for data in json.loads(categories)]
    return categories


async def cached_projects(
    redis: Redis,
    ex: timedelta = timedelta(days=1),
    *,
    prefix: str,
    categories_ids: list[int]
):
    # await redis.delete("kwork_api_categories")
    projects: list[Project] | bytes = await redis.get(prefix)
    if not projects:
        projects: list[Project] = await kwork_api.get_projects(categories_ids)
        await redis.set(prefix, json.dumps([x.json() for x in projects]), ex=ex)
    projects = [Project(**json.loads(data)) for data in json.loads(projects)]
    return projects


def get_category_name(categories: list[Category], category_id: int):
    pass
    return ""


def get_subcategory_name(categories: list[Category], subcategory_id: int):
    pass
    return ""
