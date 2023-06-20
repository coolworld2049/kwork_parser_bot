from kwork_parser_bot.bots.main_bot.main import run_main_bot
from kwork_parser_bot.core.config import get_app_settings

get_app_settings().configure_loguru()

import asyncio

from aiogram import Dispatcher
from loguru import logger

from kwork_parser_bot.bots.dispatcher import dp


async def startup(dp: Dispatcher) -> None:
    pass


async def shutdown(dp: Dispatcher) -> None:
    pass


async def main():
    await startup(dp)
    try:
        await run_main_bot()
    except BaseException as e:
        logger.warning(e.__class__.__name__)
        await shutdown(dp)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
