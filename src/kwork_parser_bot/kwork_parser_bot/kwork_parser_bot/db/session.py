from contextlib import asynccontextmanager

from asyncpg import UniqueViolationError
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from kwork_parser_bot.core.config import get_app_settings

engine = create_async_engine(get_app_settings().pgbouncer_url_async)
session = async_sessionmaker(engine, autocommit=False)


@asynccontextmanager
async def get_db() -> AsyncSession:
    s = session()
    try:
        yield s
        await s.commit()
    except Exception as e:  # noqa
        await s.rollback()
        if not e.__class__.__name__ != IntegrityError.__class__.__name__:
            logger.warning(e)
    finally:
        await s.close()
