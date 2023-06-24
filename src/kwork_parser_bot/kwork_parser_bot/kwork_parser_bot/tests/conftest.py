import asyncio
import os
import pathlib
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from redis.asyncio import ConnectionPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.db import load_all_models
from kwork_parser_bot.db.meta import meta
from kwork_parser_bot.db.utils import create_database, drop_database
from kwork_parser_bot.services.kwork.base_class import KworkCreds
from kwork_parser_bot.services.scheduler.base_class import Scheduler


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest_asyncio.fixture(scope="module")
def kwork_creds() -> KworkCreds | None:
    """
    Get instance of a KworkCreds with real creds.

    :return: KworkCreds instance.
    """
    kwork_creds = KworkCreds(
        login=get_app_settings().TEST_KWORK_LOGIN,
        password=get_app_settings().TEST_KWORK_PASSWORD,
        phone=get_app_settings().TEST_KWORK_PHONE,
    )
    return kwork_creds


@pytest_asyncio.fixture
async def fake_redis_pool() -> AsyncGenerator[ConnectionPool, None]:
    """
    Get instance of a fake redis.

    :yield: FakeRedis instance.
    """
    server = FakeServer()
    server.connected = True
    pool = ConnectionPool(connection_class=FakeConnection, server=server)
    yield pool
    await pool.disconnect()


@pytest_asyncio.fixture
async def fake_scheduler() -> AsyncGenerator[Scheduler, None]:
    """
    Get instance of a fake Scheduler.

    :yield: Scheduler instance.
    """
    scheduler = Scheduler()
    sqlite_file_path = f"{pathlib.Path(__file__).parent}/fake_jobstore.db"
    scheduler_jobstore = SQLAlchemyJobStore(f"sqlite:///{sqlite_file_path}")
    scheduler.add_jobstore(scheduler_jobstore)
    yield scheduler
    scheduler.shutdown(wait=False)
    scheduler.remove_jobstore("default")
    os.remove(sqlite_file_path)


@pytest_asyncio.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    load_all_models()
    await create_database()
    engine = create_async_engine(get_app_settings().pgbouncer_url_async)
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest_asyncio.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the tests completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    transaction = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()
