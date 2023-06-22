import logging
import os
import pathlib
import sys
from typing import Optional

from aiogram.types import BotCommand
from loguru import logger

from kwork_parser_bot.core.settings.base import BaseAppSettings

project_path = pathlib.Path(__file__).parent.parent.parent


class BotSettings(BaseAppSettings):
    BOT_TOKEN: str
    BOT_COMMANDS: list[BotCommand] = [
        BotCommand(command="/start", description="start the main_bot"),
    ]
    BOT_SUPPORT: Optional[str] = "https://t.me/kworkAdsParserSupport"


class RedisSettings(BaseAppSettings):
    USE_REDIS: Optional[bool] = True
    REDIS_MASTER_HOST: str
    REDIS_MASTER_PORT_NUMBER: int
    REDIS_MASTER_PASSWORD: str
    REDIS_PASSWORD: str
    REDIS_DATABASE: Optional[int] = 5
    REDIS_MAX_CONNECTIONS: Optional[int] = 1000


class Settings(BotSettings, RedisSettings):
    PROJECT_NAME: Optional[str] = pathlib.Path(__file__).parent
    STAGE: str
    KWORK_LOGIN: Optional[str]
    KWORK_PASSWORD: Optional[str]
    KWORK_PHONE_LAST: Optional[str]
    TIMEZONE: Optional[str] = "Europe/Moscow"
    LOG_FILE_PATH: Optional[str] = f"{project_path}/.logs/access.log"
    LOGGING_LEVEL: str = logging.getLevelName(os.getenv("LOGGING_LEVEL", "INFO"))

    class Config:
        case_sensitive = True

    def configure_loguru(self):
        logger.configure(
            handlers=[
                {
                    "sink": sys.stderr,
                    "level": self.LOGGING_LEVEL,
                },
            ],
        )
        logger.add(
            self.LOG_FILE_PATH,
            serialize=False,
            level=self.LOGGING_LEVEL,
            enqueue=True,
            backtrace=True,
            diagnose=True,
            encoding="UTF-8",
            rotation="128 MB",
            retention="14 days",
            compression="zip",
        )
