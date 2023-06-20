import asyncio

from loguru import logger

from kwork_parser_bot.db.init_db import init_db


async def main() -> None:
    logger.info("Creating initial data")
    await init_db()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
