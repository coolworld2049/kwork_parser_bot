import asyncio

from _logging import configure_logging
from bot.main import run_bot
from kwork_api.client.kwork import logger

if __name__ == "__main__":
    configure_logging()
    try:
        asyncio.run(run_bot())
    except Exception as e:
        logger.debug(e.args, exc_info=True)
    except KeyboardInterrupt:
        pass
