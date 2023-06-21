import asyncio

from aiogram import Dispatcher
from loguru import logger

from kwork_parser_bot.bots.dispatcher import dp
from kwork_parser_bot.bots.main_bot.handlers import (
    base_commands,
    kwork,
    scheduler,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot, async_scheduler
from kwork_parser_bot.core.config import get_app_settings


async def startup(dp: Dispatcher) -> None:
    if await main_bot.get_my_commands() == get_app_settings().BOT_COMMANDS:
        await main_bot.delete_my_commands()
    else:
        await main_bot.set_my_commands(commands=get_app_settings().BOT_COMMANDS)
    dp.include_routers(
        base_commands.router,
        kwork.router,
        scheduler.router,
    )
    logger.info("Start scheduler_jobs!")
    async_scheduler.start()
    logger.info("Start polling!")


async def shutdown(dp: Dispatcher) -> None:
    await dp.storage.close()
    logger.info("Stop polling!")


async def run_main_bot():
    await startup(dp)
    try:
        await dp.start_polling(main_bot, allowed_updates=dp.resolve_used_update_types())
    except BaseException as e:
        logger.warning(e.__class__.__name__)
        await shutdown(dp)


if __name__ == "__main__":
    asyncio.run(run_main_bot())
