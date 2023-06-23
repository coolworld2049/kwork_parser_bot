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
from kwork_parser_bot.services.kwork.lifetime import init_kwork_api, shutdown_kwork_api
from kwork_parser_bot.services.kwork.main import kwork_api
from kwork_parser_bot.services.redis.lifetime import init_redis, shutdown_redis
from kwork_parser_bot.services.sched.lifetime import init_sched, shutdown_sched
from kwork_parser_bot.services.sched.main import async_scheduler


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
    init_redis(main_bot)
    init_kwork_api(main_bot)
    init_sched(main_bot)
    async_scheduler.start()  # TODO: remove


async def shutdown(dp: Dispatcher) -> None:
    async_scheduler.shutdown(wait=True)  # TODO: remove
    await shutdown_redis(main_bot)
    await dp.storage.close()
    await shutdown_kwork_api(main_bot)
    await kwork_api.close()  # TODO: remove
    await shutdown_sched(main_bot)


async def run_main_bot():
    await startup(dp)
    try:
        await dp.start_polling(main_bot)
    except Exception as e:
        logger.warning(e.args)
    finally:
        await shutdown(dp)
