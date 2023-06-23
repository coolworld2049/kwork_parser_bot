from contextlib import asynccontextmanager

from loguru import logger

from kwork_parser_bot.services.kwork.base_class import KworkApi, KworkCreds


@asynccontextmanager
async def get_user_kwork_api(kwork_creds: KworkCreds):
    kwork_api = KworkApi(kwork_creds)
    try:
        yield kwork_api
    except Exception as e:
        logger.error(e.args)
    finally:
        await kwork_api.close()
