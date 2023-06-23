from aiogram import Bot
from redis.asyncio import ConnectionPool

from kwork_parser_bot.core.config import get_app_settings


def init_redis(bot: Bot):
    bot.redis_pool = ConnectionPool.from_url(
        str(get_app_settings().redis_url),
    )


async def shutdown_redis(bot: Bot):
    await bot.redis_pool.disconnect()
