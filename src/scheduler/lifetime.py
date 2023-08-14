from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from scheduler.scheduler import Scheduler
from settings import get_settings


def init_scheduler(scheduler: Scheduler) -> None:
    scheduler.add_jobstore(
        SQLAlchemyJobStore(url=get_settings().postgres_url, tablename="SchedulerJobs")
    )
    scheduler.start()


def shutdown_scheduler(scheduler) -> None:
    scheduler.shutdown(wait=False)
