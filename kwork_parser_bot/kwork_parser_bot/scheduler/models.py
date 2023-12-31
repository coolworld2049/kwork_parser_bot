from datetime import datetime
from typing import Any

from apscheduler.triggers.base import BaseTrigger
from pydantic import BaseModel

from telegram_bot.callbacks import SchedulerCallback


class SchedulerJobBase(BaseModel):
    func: Any
    trigger: str | BaseTrigger = None
    args: list | tuple = None
    kwargs: dict = None
    name: str = None
    misfire_grace_time: int = None
    coalesce: bool = None
    max_instances: int = None
    next_run_time: datetime = None
    jobstore: str = "default"
    executor: str = "default"
    replace_existing: bool = False

    class Config:
        arbitrary_types_allowed = True


class SchedulerJob(SchedulerJobBase):
    text: str
    callback: SchedulerCallback

    @property
    def id(self):
        return self.callback.pack()
