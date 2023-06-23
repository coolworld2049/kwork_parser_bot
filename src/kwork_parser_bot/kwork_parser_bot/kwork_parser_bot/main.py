import asyncio

from loguru import logger

from kwork_parser_bot._logging import configure_logging
from kwork_parser_bot.bots.main_bot.main import run_main_bot

configure_logging()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_main_bot())
    except Exception as e:
        logger.warning(e.args)
    except KeyboardInterrupt:
        pass
