from aiogram import Bot
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.services.scheduler.base_class import Scheduler

scheduler = Scheduler(timezone=get_app_settings().TIMEZONE)
scheduler_jobstore = SQLAlchemyJobStore(get_app_settings().pgbouncer_url)
scheduler.add_jobstore(scheduler_jobstore)


def init_scheduler(bot: Bot) -> None:
    bot.scheduler = scheduler
    bot.scheduler.start()


async def shutdown_scheduler(bot: Bot) -> None:
    scheduler: Scheduler = bot.scheduler  # noqa
    await scheduler.shutdown(wait=True)
