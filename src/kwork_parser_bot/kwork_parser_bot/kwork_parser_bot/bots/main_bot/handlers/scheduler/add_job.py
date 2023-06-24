from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.triggers.cron import CronTrigger

from kwork_parser_bot.bots.main_bot.callbacks import (
    SchedulerCallback,
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.handlers.menu import start_message
from kwork_parser_bot.bots.main_bot.handlers.utils import message_process
from kwork_parser_bot.bots.main_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.states import SchedulerState
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.schemas.kwork.schedjob import SchedJob
from kwork_parser_bot.services.kwork.base_class import KworkApi
from kwork_parser_bot.services.scheduler.lifetime import scheduler
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.callback_query(
    SchedulerCallback.filter(F.name == "job" and F.action == "add"),
    SchedulerState.add_job_process_input,
)
async def scheduler_add_job_trigger_process(
    query: CallbackQuery, callback_data: SchedulerCallback, state: FSMContext
):
    state_data = await state.get_data()
    builder = menu_navigation_keyboard_builder(
        back_callback=MenuCallback(name=callback_data.from_).pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    message = await main_bot.send_message(
        query.from_user.id,
        render_template(
            "cron.html",
        ),
        reply_markup=builder.as_markup(),
    )
    await query.message.delete()
    await state.set_state(SchedulerState.add_job)


@router.message(SchedulerState.add_job)
@message_process
async def scheduler_add_job_process(
    message: Message, state: FSMContext, kwork_api: KworkApi
):
    state_data = await state.get_data()
    sched_jobs: list[SchedJob] = [SchedJob(**x) for x in state_data.get("sched_jobs")]
    for sched_job in sched_jobs:
        cron_trigger = CronTrigger(jitter=120).from_crontab(
            message.text, timezone=get_app_settings().TIMEZONE
        )
        sched_job.func = sched_job.func
        sched_job.trigger = cron_trigger
        sched_job_data: dict = sched_job.dict(exclude_none=True)
        sched_job_data.update({"id": sched_job.id})
        scheduler.add_job(**sched_job_data)
        await start_message(message, state, kwork_api)
