from aiogram import Dispatcher
from aiogram.types import BotCommand
from aredis_om import Migrator

from kwork_parser_bot.bot import loader
from kwork_parser_bot.bot.dispatcher import dp
from kwork_parser_bot.bot.handlers import menu, kwork, scheduler
from kwork_parser_bot.bot.loader import main_bot
from kwork_parser_bot.services.scheduler.lifetime import (
    init_scheduler,
    shutdown_scheduler,
)
from kwork_parser_bot.settings import settings


async def set_bot_commands(commands: list[BotCommand]):
    if await main_bot.get_my_commands() == commands:
        await main_bot.delete_my_commands()
    else:
        await main_bot.set_my_commands(commands)


async def startup(dp: Dispatcher) -> None:
    await main_bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(settings().BOT_COMMANDS)
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


async def run_main_bot():
    try:
        await startup(dp)
        await dp.start_polling(main_bot)
    finally:
        await shutdown(dp)
