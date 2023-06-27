import asyncio
import os
import pathlib
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from aredis_om import Migrator
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from redis.asyncio import ConnectionPool

from kwork_parser_bot.services.kwork.schemas import KworkAccount
from kwork_parser_bot.services.scheduler.scheduler import Scheduler
from kwork_parser_bot.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest_asyncio.fixture(scope="module")
def kwork_account() -> KworkAccount | None:
    kwork_account = KworkAccount(
        telegram_user_id=settings().BOT_OWNER_ID,
        login=settings().TEST_KWORK_LOGIN,
        password=settings().TEST_KWORK_PASSWORD,
        phone=settings().TEST_KWORK_PHONE,
    )
    return kwork_account


@pytest_asyncio.fixture
async def fake_redis_pool() -> AsyncGenerator[ConnectionPool, None]:
    server = FakeServer()
    server.connected = True
    pool = ConnectionPool(connection_class=FakeConnection, server=server)
    await Migrator().run()
    yield pool
    await pool.disconnect()


@pytest_asyncio.fixture
async def fake_scheduler() -> AsyncGenerator[Scheduler, None]:
    scheduler = Scheduler()
    sqlite_file_path = f"{pathlib.Path(__file__).parent}/fake_jobstore.db"
    scheduler_jobstore = SQLAlchemyJobStore(f"sqlite:///{sqlite_file_path}")
    scheduler.add_jobstore(scheduler_jobstore)
    yield scheduler
    try:
        scheduler.shutdown()
        scheduler.remove_jobstore("default")
        os.remove(sqlite_file_path)
    except* (AttributeError, FileNotFoundError):
        pass
