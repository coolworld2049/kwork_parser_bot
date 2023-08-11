from aiogram import Dispatcher
from aredis_om import Migrator

from bot import loader
from bot.dispatcher import dp
from bot.handlers import menu, kwork, scheduler
from bot.loader import main_bot
from scheduler.lifetime import (
    init_scheduler,
    shutdown_scheduler,
)
from settings import settings


async def startup(dp: Dispatcher) -> None:
    await main_bot.delete_webhook(drop_pending_updates=True)
    if not await main_bot.get_my_commands() == settings().BOT_COMMANDS:
        await main_bot.delete_my_commands()
        await main_bot.set_my_commands(settings().BOT_COMMANDS)
    init_scheduler(loader.scheduler)
    dp.include_routers(
        menu.router,
        kwork.router,
        scheduler.router,
    )
    await Migrator().run()


async def shutdown(dp: Dispatcher) -> None:
    await dp.storage.close()
    shutdown_scheduler(loader.scheduler)


async def run_bot():
    try:
        await startup(dp)
        await dp.start_polling(main_bot, polling_timeout=5)
    finally:
        await shutdown(dp)
