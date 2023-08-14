import pathlib
from functools import lru_cache
from typing import Optional, Literal

from aiogram.types import BotCommand
from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn

load_dotenv()


class SchedulerSettings(BaseSettings):
    SCHED_JOBS_MODULE = f"scheduler.jobs"


class BotSettings(BaseSettings):
    BOT_TOKEN: str
    BOT_RUN_MODE: Literal["webhook", "polling"] = "polling"
    BOT_ACL_USER_IDS: Optional[list[int]] = None
    BOT_ACL_ENABLED: Literal["True", "true", "False", "false"] = "false"
    BOT_COMMANDS: list[BotCommand] = [
        BotCommand(command="/start", description="start bot"),
        BotCommand(command="/help", description="get help"),
    ]
    NOTIFICATION_CHANNEL_ID: Optional[int] = None
    WEBHOOK_URL: Optional[str] = None
    WEB_APP_HOST: Optional[str] = "0.0.0.0"
    WEB_APP_PORT: Optional[int] = 8000

    @property
    def webhook_url(self):
        return f"{self.WEBHOOK_URL}/telegram_bot{self.BOT_TOKEN}"

    @property
    def is_bot_acl_enabled(self):
        if self.BOT_ACL_ENABLED in ["True", "true"]:
            return True
        elif self.BOT_ACL_ENABLED in ["False", "false"]:
            return False


class RedisSettings(BaseSettings):
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


class DatabaseSettings(BaseSettings):
    POSTGRESQL_MASTER_HOST: str = "localhost"
    POSTGRESQL_MASTER_PORT: Optional[int] = 5432
    POSTGRESQL_DATABASE: Optional[str] = "app"
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str

    @property
    def postgres_url(self) -> str:
        dsn = PostgresDsn.build(
            scheme="postgresql",
            user=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_MASTER_HOST,
            port=str(self.POSTGRESQL_MASTER_PORT),
            path=f"/{self.POSTGRESQL_DATABASE}",
        )
        return dsn

    @property
    def postgres_asyncpg_url(self) -> str:
        return self.postgres_url.replace("://", "+asyncpg://")


class Settings(BotSettings, SchedulerSettings, RedisSettings, DatabaseSettings):
    LOG_FILE_PATH: Optional[str] = f"{pathlib.Path(__file__).parent.parent}/.logs"
    LOGGING_LEVEL: Optional[str] = "INFO"
    TIMEZONE: Optional[str] = "Europe/Moscow"


@lru_cache
def get_settings() -> Settings:
    config = Settings
    return config()
