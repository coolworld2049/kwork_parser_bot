from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from kwork_parser_bot.core.config import get_app_settings

main_bot = Bot(get_app_settings().BOT_TOKEN, parse_mode="HTML")
async_scheduler = AsyncIOScheduler(timezone=get_app_settings().TIMEZONE)
async_scheduler.add_jobstore(
    "sqlalchemy",
    url=f"sqlite:///{get_app_settings().pkg_path}/{get_app_settings().PROJECT_NAME}_jobstore.sqlite",
)
