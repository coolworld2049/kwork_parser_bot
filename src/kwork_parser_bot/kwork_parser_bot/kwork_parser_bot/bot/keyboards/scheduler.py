from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from kwork_parser_bot.bot.callbacks import SchedulerCallback
from kwork_parser_bot.services.scheduler.schemas import SchedulerJob


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
    sched_jobs: list[SchedulerJob],
):
    builder = InlineKeyboardBuilder()
    for sched_job in sched_jobs:
        builder.add(
            InlineKeyboardButton(
                text=sched_job.text,
                callback_data=sched_job.callback.pack(),
            )
        )
    builder.adjust(1)
    return builder
