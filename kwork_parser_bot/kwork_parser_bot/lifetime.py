from aiogram import Dispatcher
from aredis_om import Migrator

import loader
from _logging import configure_logging
from loader import bot
from scheduler.lifetime import (
    init_scheduler,
    shutdown_scheduler,
)
from settings import get_settings
from telegram_bot.handlers import kwork, scheduler, settings, menu


async def startup_bot(dp: Dispatcher) -> None:
    configure_logging()
    await bot.delete_my_commands()
    await bot.set_my_commands(get_settings().BOT_COMMANDS)
    init_scheduler(loader.scheduler)
    dp.include_routers(menu.router, kwork.router, scheduler.router, settings.router)

    await Migrator().run()
    await loader.prisma.connect()


async def shutdown_bot(dp: Dispatcher) -> None:
    if loader.prisma.is_connected():
        await loader.prisma.disconnect()
    await dp.storage.close()
    shutdown_scheduler(loader.scheduler)
