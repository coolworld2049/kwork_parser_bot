from aiogram import Bot
from redis.asyncio import ConnectionPool

from kwork_parser_bot.core.config import get_app_settings

redis_pool = ConnectionPool.from_url(
    get_app_settings().redis_url,
)


def init_redis(bot: Bot):
    bot.redis_pool = redis_pool


async def shutdown_redis(bot: Bot):
    redis_pool: ConnectionPool = bot.redis_pool  # noqa
    await redis_pool.disconnect()
