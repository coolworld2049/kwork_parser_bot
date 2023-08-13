import time
from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy import event, exc
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from settings import settings

engine = create_async_engine(settings().postgres_asyncpg_url)
session = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_db() -> AsyncSession:
    s = session()
    try:
        yield s
    except exc.SQLAlchemyError as e:
        await s.rollback()
        logger.debug(f"{e.__class__} {e} - ROLLBACK")
    finally:
        await s.close()
