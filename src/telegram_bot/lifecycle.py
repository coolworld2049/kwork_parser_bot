from aiogram import Dispatcher
from aredis_om import Migrator

from _logging import configure_logging
from telegram_bot import loader
from telegram_bot.dispatcher import dp
from telegram_bot.handlers import menu, kwork, scheduler
from telegram_bot.loader import bot
from scheduler.lifetime import (
    init_scheduler,
    shutdown_scheduler,
)
from settings import settings


async def startup_bot(dp: Dispatcher) -> None:
    configure_logging()
    if not await bot.get_my_commands() == settings().BOT_COMMANDS:
        await bot.delete_my_commands()
        await bot.set_my_commands(settings().BOT_COMMANDS)
    await Migrator().run()
    init_scheduler(loader.scheduler)
    dp.include_routers(
        menu.router,
        kwork.router,
        scheduler.router,
    )


async def shutdown_bot(dp: Dispatcher) -> None:
    await dp.storage.close()
    shutdown_scheduler(loader.scheduler)
