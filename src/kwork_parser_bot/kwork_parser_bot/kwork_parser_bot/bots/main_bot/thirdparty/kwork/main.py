import json
from datetime import timedelta

from kwork import Kwork
from kwork.types import Category
from redis.asyncio.client import Redis

from kwork_parser_bot.core.config import get_app_settings

kwork_api = Kwork(
    login=get_app_settings().KWORK_LOGIN, password=get_app_settings().KWORK_PASSWORD
)


async def get_categories(redis: Redis, ex: timedelta = timedelta(days=1)):
    # await redis.delete("kwork_api_categories")
    categories: list[Category] | bytes = await redis.get("kwork_api_categories")
    if not categories:
        categories: list[Category] = await kwork_api.get_categories()
        await redis.set("kwork_api_categories", json.dumps([x.json() for x in categories]), ex=ex)
    categories = [Category(**json.loads(data)) for data in json.loads(categories)]
    return categories
