from aiogram import Dispatcher
from loguru import logger

from kwork_parser_bot.bots.dispatcher import dp
from kwork_parser_bot.bots.main_bot.handlers import (
    scheduler,
    menu,
    kwork,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.services.redis.lifetime import init_redis, shutdown_redis
from kwork_parser_bot.services.scheduler.lifetime import (
    init_scheduler,
    shutdown_scheduler,
)


async def startup(dp: Dispatcher) -> None:
    await main_bot.delete_webhook(drop_pending_updates=True)
    if await main_bot.get_my_commands() == get_app_settings().BOT_COMMANDS:
        await main_bot.delete_my_commands()
    else:
        await main_bot.set_my_commands(commands=get_app_settings().BOT_COMMANDS)
    init_scheduler()
    init_redis(main_bot)
    dp.include_routers(
        menu.router,
        kwork.menu.router,
        kwork.category.router,
        kwork.auth.router,
        scheduler.menu.router,
        scheduler.add_job.router,
        scheduler.remove_job.router,
    )


async def shutdown(dp: Dispatcher) -> None:
    await dp.storage.close()
    await shutdown_scheduler()
    await shutdown_redis(main_bot)


async def run_main_bot():
    await startup(dp)
    try:
        await dp.start_polling(main_bot)
    except Exception as e:
        logger.error(e.args)
    finally:
        await shutdown(dp)
