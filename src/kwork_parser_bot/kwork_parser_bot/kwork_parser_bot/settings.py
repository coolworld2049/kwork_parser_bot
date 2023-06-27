import logging
import os
import pathlib
from functools import lru_cache
from typing import Optional

from aiogram.types import BotCommand
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseSettings

project_path = pathlib.Path(__file__).parent.parent.parent


class BaseAppSettings(BaseSettings):
    load_dotenv(find_dotenv(f"{project_path}/.env"))
    stage_dotenv = find_dotenv(f'{project_path}/.env.{os.getenv("STAGE", "dev")}')
    load_dotenv(stage_dotenv, override=True) if stage_dotenv else None


class SchedulerSettings(BaseAppSettings):
    SCHED_JOBS_MODULE = f"{__package__}.services.scheduler.jobs"


class BotSettings(BaseAppSettings):
    BOT_OWNER_ID: int
    BOT_TOKEN: str
    BOT_COMMANDS: list[BotCommand] = [
        BotCommand(command="/start", description="start the bot"),
    ]
    NOTIFICATION_CHANNEL_ID: Optional[int] = None


class RedisSettings(BaseAppSettings):
    REDIS_MASTER_HOST: str
    REDIS_MASTER_PORT_NUMBER: Optional[int] = 6379
    REDIS_USERNAME: Optional[str] = "default"
    REDIS_PASSWORD: Optional[str]

    @property
    def redis_url(self):
        password = (
            f"{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}@"
            if self.REDIS_PASSWORD
            else ""
        )
        return f"redis://{password}{self.REDIS_MASTER_HOST}:{self.REDIS_MASTER_PORT_NUMBER}/0"

    REDIS_OM_URL: Optional[str]


class Settings(BotSettings, SchedulerSettings, RedisSettings):
    PROJECT_NAME: Optional[str] = pathlib.Path(__file__).parent
    STAGE: str
    LOG_FILE_PATH: Optional[str] = f"{project_path}/.logs"
    LOGGING_LEVEL: Optional[str] = logging.getLevelName(
        os.getenv("LOGGING_LEVEL", "INFO")
    )
    TIMEZONE: Optional[str] = "Europe/Moscow"
    TEST_KWORK_LOGIN: Optional[str]
    TEST_KWORK_PASSWORD: Optional[str]
    TEST_KWORK_PHONE: Optional[str]


@lru_cache
def settings() -> Settings:
    config = Settings
    return config()
