import asyncio

from loguru import logger

from kwork_parser_bot.db.utils import create_database


async def main() -> None:
    logger.info("Creating initial data")
    await create_database()
    logger.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
