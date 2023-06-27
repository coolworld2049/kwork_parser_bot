from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger


class Scheduler(AsyncIOScheduler):
    def __init__(self, **options):
        super().__init__(**options)

    def get_user_job(self, user_id: int, job_id: str = None):
        jobs = self.get_jobs()
        jobs = list(filter(lambda x: str(user_id) in x.id, jobs))
        if job_id:
            jobs = self.get_job(job_id)
        return jobs

    def remove_user_job(self, user_id: int, job_id: str | list[str]):
        results = []
        if not isinstance(job_id, list):
            job_id = [job_id]
        for id in job_id:
            try:
                if str(user_id) in id:
                    self.remove_job(id)
                else:
                    raise
                results.append(f"✔️ {id}")
            except Exception as e:
                logger.debug(e)
                results.append(f"❌ {id}")
        return results
