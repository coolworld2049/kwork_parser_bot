import logging
import os
import pathlib
from typing import Optional

import pydantic
from aiogram.types import BotCommand
from pydantic import PostgresDsn
from yarl import URL

from kwork_parser_bot.core.settings.base import BaseAppSettings

project_path = pathlib.Path(__file__).parent.parent.parent


class SettingsBase(BaseAppSettings):
    TIMEZONE: Optional[str] = "Europe/Moscow"
    LOG_FILE_PATH: Optional[str] = f"{project_path}/.logs"
    LOGGING_LEVEL: Optional[str] = logging.getLevelName(os.getenv("LOGGING_LEVEL", "INFO"))


class MainBotSettings(SettingsBase):
    BOT_TOKEN: str
    BOT_COMMANDS: list[BotCommand] = [
        BotCommand(command="/start", description="start the main_bot"),
    ]
    BOT_SUPPORT: Optional[str] = "https://t.me/kworkAdsParserSupport"


class RedisSettings(SettingsBase):
    USE_REDIS: Optional[bool] = True
    REDIS_MASTER_HOST: str
    REDIS_MASTER_PORT_NUMBER: int
    REDIS_MASTER_PASSWORD: str
    REDIS_PASSWORD: str
    REDIS_DATABASE: Optional[int] = 5
    REDIS_MAX_CONNECTIONS: Optional[int] = 1000


class PostgresSettings(SettingsBase):
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_DATABASE: str
    POSTGRESQL_MASTER_HOST: str
    POSTGRESQL_MASTER_PORT_NUMBER: Optional[int] = 5432

    @property
    def postgresql_timezone(self):
        return self.TIMEZONE


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


class Settings(MainBotSettings, RedisSettings, PgbouncerSettings):
    PROJECT_NAME: Optional[str] = pathlib.Path(__file__).parent
    STAGE: str
    KWORK_LOGIN: Optional[str]
    KWORK_PASSWORD: Optional[str]
    KWORK_PHONE_LAST: Optional[str]

    class Config:
        case_sensitive = True
