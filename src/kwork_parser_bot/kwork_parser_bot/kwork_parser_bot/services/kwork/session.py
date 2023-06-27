from contextlib import asynccontextmanager
from typing import AsyncGenerator

from loguru import logger

from kwork_parser_bot.services.kwork.kwork import KworkApi
from kwork_parser_bot.services.kwork.schemas import KworkAccount


@asynccontextmanager
async def get_kwork_api(
    kwork_account: KworkAccount,
) -> AsyncGenerator[KworkApi, None]:
    kwork_api = KworkApi(kwork_account)
    try:
        yield kwork_api
    except Exception as e:
        logger.debug(e)
        raise e
    finally:
        await kwork_api.close()
