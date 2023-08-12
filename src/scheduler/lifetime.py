from apscheduler.jobstores.redis import RedisJobStore

from scheduler.scheduler import Scheduler
from settings import settings


def init_scheduler(scheduler: Scheduler) -> None:
    scheduler_jobstore = RedisJobStore(
        host=settings().REDIS_MASTER_HOST,
        port=settings().REDIS_MASTER_PORT_NUMBER,
        password=settings().REDIS_PASSWORD,
    )
    scheduler.add_jobstore(scheduler_jobstore)
    scheduler.start()


def shutdown_scheduler(scheduler) -> None:
    scheduler.shutdown(wait=False)
