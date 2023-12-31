import random
from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.triggers.cron import CronTrigger
from prisma.models import BotUser

from loader import bot, scheduler
from scheduler.models import SchedulerJob
from telegram_bot.callbacks import (
    SchedulerCallback,
    MenuCallback,
)
from telegram_bot.handlers.decorators import message_process_error
from telegram_bot.handlers.menu import start_message
from telegram_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from telegram_bot.states import SchedulerState
from template_engine import render_template

router = Router(name=__file__)


@router.callback_query(
    SchedulerCallback.filter(F.name == "job" and F.action == "add"),
    SchedulerState.add_job_process_input,
)
async def scheduler_add_job_trigger_process(
    query: CallbackQuery, callback_data: SchedulerCallback, state: FSMContext
):
    state_data = await state.get_data()
    bot_user = await BotUser.prisma().find_unique(where={"id": query.from_user.id})
    builder = menu_navigation_keyboard_builder(
        back_callback=MenuCallback(name=callback_data.from_).pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    message = await bot.send_message(
        query.from_user.id,
        render_template("cron.html", timezone=bot_user.settings.get("timezone")),
        reply_markup=builder.as_markup(),
    )
    await query.message.delete()
    await state.set_state(SchedulerState.add_job)


@router.message(SchedulerState.add_job)
@message_process_error
async def scheduler_add_job_process(message: Message, state: FSMContext):
    bot_user = await BotUser.prisma().find_unique(where={"id": message.from_user.id})
    cron_trigger = CronTrigger(jitter=random.randint(120, 180)).from_crontab(
        message.text, timezone=bot_user.settings.get("timezone")
    )
    state_data = await state.get_data()
    sched_job = SchedulerJob(**state_data.get("sched_job"))
    sched_job.trigger = cron_trigger
    sched_job_data: dict = sched_job.dict(exclude_none=True)
    sched_job_data.update({"id": sched_job.id})
    scheduler.add_job(**sched_job_data)
    await state.clear()
    await message.delete()
    await start_message(message, state)
