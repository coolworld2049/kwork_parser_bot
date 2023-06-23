from aiogram import Dispatcher
from loguru import logger

from kwork_parser_bot.bots.dispatcher import dp
from kwork_parser_bot.bots.main_bot.handlers import (
    kwork,
    scheduler,
    menu,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.services.redis.lifetime import init_redis, shutdown_redis
from kwork_parser_bot.services.scheduler.lifetime import init_scheduler, shutdown_scheduler


async def startup(dp: Dispatcher) -> None:
    if await main_bot.get_my_commands() == get_app_settings().BOT_COMMANDS:
        await main_bot.delete_my_commands()
    else:
        await main_bot.set_my_commands(commands=get_app_settings().BOT_COMMANDS)
    await main_bot.delete_webhook(drop_pending_updates=True)
    init_redis(main_bot)
    init_scheduler(main_bot)
    dp.include_routers(
        menu.router,
        kwork.router,
        scheduler.router,
    )


async def shutdown(dp: Dispatcher) -> None:
    await dp.storage.close()
    await shutdown_redis(main_bot)
    await shutdown_scheduler(main_bot)


async def run_main_bot():
    await startup(dp)
    try:
        await dp.start_polling(main_bot)
    except Exception as e:
        logger.warning(e.args)
    finally:
        await shutdown(dp)
