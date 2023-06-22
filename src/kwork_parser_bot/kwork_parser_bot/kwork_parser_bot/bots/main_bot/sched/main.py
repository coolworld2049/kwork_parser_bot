from loguru import logger

from kwork_parser_bot.bots.main_bot.loader import async_scheduler


async def remove_job(job_id: str | list[str]):
    results = []
    if not isinstance(job_id, list):
        job_id = [job_id]
    for id in job_id:
        prev_not_found = False
        if not async_scheduler.get_job(id):
            results.append(f"{id} not found")
            prev_not_found = True
        try:
            async_scheduler.remove_job(id)
        except Exception as e:
            logger.debug(e)
        if not async_scheduler.get_job(id) and not prev_not_found:
            results.append(f"{id} successfully deleted")
    return results
