from aiogram import Dispatcher
from loguru import logger

from kwork_parser_bot.bots.dispatcher import dp
from kwork_parser_bot.bots.main_bot.handlers import (
    kwork,
    scheduler, menu,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot, async_scheduler
from kwork_parser_bot.bots.main_bot.thirdparty.kwork.main import kwork_api
from kwork_parser_bot.core.config import get_app_settings


async def startup(dp: Dispatcher) -> None:
    if await main_bot.get_my_commands() == get_app_settings().BOT_COMMANDS:
        await main_bot.delete_my_commands()
    else:
        await main_bot.set_my_commands(commands=get_app_settings().BOT_COMMANDS)
    await main_bot.delete_webhook(drop_pending_updates=True)
    dp.include_routers(
        menu.router,
        kwork.router,
        scheduler.router,
    )
    async_scheduler.start()


async def shutdown(dp: Dispatcher) -> None:
    async_scheduler.shutdown(wait=True)
    await dp.storage.close()
    await kwork_api.close()


async def run_main_bot():
    await startup(dp)
    try:
        await dp.start_polling(main_bot)
    except Exception as e:
        logger.warning(e.args)
    else:
        await shutdown(dp)
