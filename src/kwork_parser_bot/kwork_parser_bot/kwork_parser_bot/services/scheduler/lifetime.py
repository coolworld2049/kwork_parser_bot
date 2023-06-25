from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.services.scheduler.main import Scheduler

scheduler = Scheduler(timezone=get_app_settings().TIMEZONE)


def init_scheduler() -> None:
    scheduler_jobstore = SQLAlchemyJobStore(get_app_settings().pgbouncer_url)
    scheduler.add_jobstore(scheduler_jobstore)
    scheduler.start()


async def shutdown_scheduler() -> None:
    await scheduler.shutdown(wait=True)
