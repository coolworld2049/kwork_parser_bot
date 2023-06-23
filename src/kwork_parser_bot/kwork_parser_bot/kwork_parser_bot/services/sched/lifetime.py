from aiogram import Bot
from redis.asyncio import ConnectionPool

from kwork_parser_bot.core.config import get_app_settings


def init_sched(bot: Bot) -> None:
    bot.sched = ConnectionPool.from_url(
        str(get_app_settings().redis_url),
    )


async def shutdown_sched(bot: Bot) -> None:
    await bot.sched.shutdown(wait=True)
