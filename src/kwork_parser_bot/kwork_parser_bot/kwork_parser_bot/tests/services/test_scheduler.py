from datetime import timedelta, datetime

import pytest
import pytz
from loguru import logger

from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.services.kwork.main import KworkCreds
from kwork_parser_bot.services.scheduler.main import Scheduler
from kwork_parser_bot.services.scheduler.jobs import (
    notify_about_kwork_notifications,
    notify_about_new_projects,
)


async def fake_job():
    a = 1 + 1
    logger.debug(f"1+1={a}")
    return a


@pytest.mark.asyncio
async def test_scheduler(fake_scheduler: Scheduler):
    fake_scheduler.start()
    datetime_now = datetime.now(tz=pytz.timezone(get_app_settings().TIMEZONE))
    job = fake_scheduler.add_job(fake_job, "interval", seconds=4, id=fake_job.__name__)
    assert job.next_run_time >= datetime_now + timedelta(seconds=2)


@pytest.mark.asyncio
async def test_scheduler_jobs(fake_scheduler: Scheduler, kwork_creds: KworkCreds):
    notifications = await notify_about_kwork_notifications(
        kwork_creds.dict(),
        get_app_settings().BOT_OWNER_ID,
        get_app_settings().BOT_OWNER_ID,
        send_message=False,
    )
    assert len(notifications) > 0
    projects = await notify_about_new_projects(
        kwork_creds.dict(),
        get_app_settings().BOT_OWNER_ID,
        get_app_settings().BOT_OWNER_ID,
        [11],
        job_id=None,
        send_message=False,
    )
    assert len(projects) > 0
