import logging
import os
import pathlib
from typing import Optional

from aiogram.types import BotCommand
from pydantic import PostgresDsn

from kwork_parser_bot.core.settings.base import BaseAppSettings

project_path = pathlib.Path(__file__).parent.parent.parent


class SchedulerSettings(BaseAppSettings):
    SCHED_JOBS_MODULE = (
        f"{'.'.join(str(__package__).split('.')[:-2])}.services.scheduler.jobs"
    )


class MainBotSettings(SchedulerSettings):
    BOT_OWNER_ID: int
    BOT_SUPPORT_USERNAME: Optional[str]
    BOT_TOKEN: str
    BOT_COMMANDS: list[BotCommand] = [
        BotCommand(command="/start", description="start the main_bot"),
    ]
    BOT_SUPPORT: Optional[str] = f"https://t.me/{os.getenv('BOT_SUPPORT_USERNAME')}"
    NOTIFICATION_CHANNEL_ID: Optional[int] = None


class RedisSettings(BaseAppSettings):
    REDIS_MASTER_HOST: str
    REDIS_MASTER_PORT_NUMBER: int
    REDIS_MASTER_PASSWORD: str
    REDIS_PASSWORD: str
    REDIS_DATABASE: Optional[int] = 5
    REDIS_MAX_CONNECTIONS: Optional[int] = 1000

    @property
    def redis_url(self):
        return (
            f"redis://:{self.REDIS_MASTER_PASSWORD}@"
            f"{self.REDIS_MASTER_HOST}:{self.REDIS_MASTER_PORT_NUMBER}"
            f"/{self.REDIS_DATABASE}"
        )


class PostgresSettings(BaseAppSettings):
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_DATABASE: str
    POSTGRESQL_MASTER_HOST: str
    POSTGRESQL_MASTER_PORT_NUMBER: Optional[int] = 5432


class PgbouncerSettings(PostgresSettings):
    PGBOUNCER_HOST: str
    PGBOUNCER_PORT: Optional[int] = 6432
    PGBOUNCER_DATABASE: str

    @property
    def pgbouncer_url(self):
        return PostgresDsn.build(
            scheme="postgresql",
            host=self.PGBOUNCER_HOST,
            port=self.PGBOUNCER_PORT.__str__(),
            user=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            path=f"/{self.POSTGRESQL_DATABASE}",
        )

    @property
    def pgbouncer_url_async(self):
        return self.pgbouncer_url.replace("postgresql", "postgresql+asyncpg")


class Settings(MainBotSettings, RedisSettings, PgbouncerSettings):
    PROJECT_NAME: Optional[str] = pathlib.Path(__file__).parent
    STAGE: str
    TIMEZONE: Optional[str] = "Europe/Moscow"
    LOG_FILE_PATH: Optional[str] = f"{project_path}/.logs"
    LOGGING_LEVEL: Optional[str] = logging.getLevelName(
        os.getenv("LOGGING_LEVEL", "INFO")
    )
    TEST_KWORK_LOGIN: Optional[str]
    TEST_KWORK_PASSWORD: Optional[str]
    TEST_KWORK_PHONE: Optional[str]
    TEST_DATA: Optional[bool] = False
