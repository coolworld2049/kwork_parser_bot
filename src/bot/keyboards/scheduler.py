from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import SchedulerCallback
from scheduler.models import SchedulerJob


def scheduler_menu_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🗑️ Remove",
            callback_data=SchedulerCallback(name="job", action="rm").pack(),
        )
    )
    return builder


def scheduler_jobs_keyboard_builder(
    sched_job: SchedulerJob,
):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=sched_job.text,
            callback_data=sched_job.callback.pack(),
        )
    )
    builder.adjust(1)
    return builder
