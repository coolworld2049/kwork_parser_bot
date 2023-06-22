from loguru import logger
import asyncio

from kwork_parser_bot.bots.main_bot.main import run_main_bot
from kwork_parser_bot.core.config import get_app_settings

get_app_settings().configure_loguru()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_main_bot())
    except Exception as e:
        logger.warning(e.args)
