from aiogram import Dispatcher
from aredis_om import Migrator

import loader
from _logging import configure_logging
from loader import bot
from scheduler.lifetime import (
    init_scheduler,
    shutdown_scheduler,
)
from settings import settings
from telegram_bot.handlers import menu, kwork, scheduler


async def startup_bot(dp: Dispatcher) -> None:
    configure_logging()
    if not await bot.get_my_commands() == settings().BOT_COMMANDS:
        await bot.delete_my_commands()
        await bot.set_my_commands(settings().BOT_COMMANDS)
    init_scheduler(loader.scheduler)
    dp.include_routers(
        menu.router,
        kwork.router,
        scheduler.router,
    )
    await Migrator().run()
    await loader.prisma.connect()


async def shutdown_bot(dp: Dispatcher) -> None:
    if loader.prisma.is_connected():
        await loader.prisma.disconnect()
    await dp.storage.close()
    shutdown_scheduler(loader.scheduler)
