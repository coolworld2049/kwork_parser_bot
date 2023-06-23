import asyncio

from kwork_parser_bot._logging import configure_logging
from kwork_parser_bot.bots.main_bot.main import run_main_bot

if __name__ == "__main__":
    configure_logging()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_main_bot())
