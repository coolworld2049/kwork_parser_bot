from contextlib import asynccontextmanager
from typing import AsyncGenerator

from loguru import logger

from kwork_parser_bot.services.kwork.main import KworkApi, KworkCreds


@asynccontextmanager
async def get_kwork_api(kwork_creds: KworkCreds) -> AsyncGenerator[KworkApi, None]:
    kwork_api = KworkApi(kwork_creds)
    try:
        yield kwork_api
    except Exception as e:
        logger.error(e.args)
        raise e
    finally:
        await kwork_api.close()
