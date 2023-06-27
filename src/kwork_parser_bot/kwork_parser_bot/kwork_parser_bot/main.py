import asyncio

from kwork_parser_bot._logging import configure_logging
from kwork_parser_bot.bot.main import run_main_bot
from kwork_parser_bot.services.kwork.api.kwork import logger

if __name__ == "__main__":
    configure_logging()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_main_bot())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.debug(e.args, exc_info=True)
