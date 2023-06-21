from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from kwork_parser_bot.core.config import get_app_settings

engine = create_async_engine(
    f"sqlite+aiosqlite:///{get_app_settings().pkg_path}/db/{get_app_settings().PROJECT_NAME}.sqlite",
    echo=True,
)
session = async_sessionmaker(engine, autocommit=False)


@asynccontextmanager
async def get_db() -> AsyncSession:
    s = session()
    try:
        yield s
        await s.commit()
    except Exception as e:  # noqa
        await s.rollback()
        logger.exception(e)
    finally:
        await s.close()
