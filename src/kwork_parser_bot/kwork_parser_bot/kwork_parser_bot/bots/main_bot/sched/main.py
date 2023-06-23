from loguru import logger

from kwork_parser_bot.bots.main_bot.loader import async_scheduler


def get_user_job(user_id: int, job_id: str = None):
    jobs = async_scheduler.get_jobs()
    jobs = list(filter(lambda x: str(user_id) in x.id, jobs))
    if job_id:
        jobs = async_scheduler.get_job(job_id)
    return jobs


def remove_job(user_id: int, job_id: str | list[str]):
    results = []
    if not isinstance(job_id, list):
        job_id = [job_id]
    for id in job_id:
        try:
            if str(user_id) in id:
                async_scheduler.remove_job(id)
            else:
                raise
            results.append(f"{id} successfully deleted!")
        except Exception as e:
            logger.debug(e)
            results.append(f"{id} not deleted!")
    return results
