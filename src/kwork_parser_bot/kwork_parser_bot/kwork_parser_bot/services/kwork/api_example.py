import asyncio
import logging

from kwork import Kwork
from kwork_parser_bot.core.config import get_app_settings

logging.basicConfig(level=logging.INFO)


async def main():
    api = Kwork(
        login=get_app_settings().TEST_KWORK_LOGIN,
        password=get_app_settings().TEST_KWORK_PASSWORD,
    )
    projects = await api.get_projects(categories_ids=[41])
    await api.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
