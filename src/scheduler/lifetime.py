from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from scheduler.scheduler import Scheduler
from settings import settings


def init_scheduler(scheduler: Scheduler) -> None:
    scheduler.add_jobstore(SQLAlchemyJobStore(url=settings().postgres_url))
    scheduler.start()


def shutdown_scheduler(scheduler) -> None:
    scheduler.shutdown(wait=False)
