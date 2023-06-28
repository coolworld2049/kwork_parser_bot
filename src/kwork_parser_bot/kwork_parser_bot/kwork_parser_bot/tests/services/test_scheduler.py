from datetime import timedelta, datetime

import pytest
import pytz
from loguru import logger

from kwork_parser_bot.services.kwork.schemas import KworkAccount
from kwork_parser_bot.services.scheduler.jobs import (
    notify_about_new_projects,
)
from kwork_parser_bot.services.scheduler.scheduler import Scheduler
from kwork_parser_bot.settings import settings


async def fake_job():
    a = 1 + 1
    logger.debug(f"1+1={a}")
    return a


@pytest.mark.asyncio
async def test_scheduler(event_loop, fake_scheduler: Scheduler):
    fake_scheduler.start()
    datetime_now = datetime.now(tz=pytz.timezone(settings().TIMEZONE))
    job = fake_scheduler.add_job(fake_job, "interval", seconds=4, id=fake_job.__name__)
    assert job.next_run_time >= datetime_now + timedelta(seconds=2)


@pytest.mark.asyncio
async def test_scheduler_jobs(
    event_loop, fake_scheduler: Scheduler, kwork_account: KworkAccount
):
    projects = await notify_about_new_projects(
        kwork_account.dict(),
        settings().BOT_OWNER_ID,
        settings().BOT_OWNER_ID,
        [41],
        job_id=None,
        send_message=False,
    )
