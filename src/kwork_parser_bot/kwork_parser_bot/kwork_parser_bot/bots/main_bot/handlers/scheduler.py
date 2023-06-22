import asyncio
import html
from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from apscheduler.triggers.cron import CronTrigger

from kwork_parser_bot.bots.main_bot.callbacks import (
    SchedulerCallback,
    MenuCallback,
    ConfirmCallback,
    CategoryCallback,
)
from kwork_parser_bot.bots.main_bot.handlers.start import start_callback, start_message
from kwork_parser_bot.bots.main_bot.keyboards.confirm import confirm_keyboard_builder
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.scheduler import (
    scheduler_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot, async_scheduler
from kwork_parser_bot.bots.main_bot.sched.main import remove_job, get_user_job
from kwork_parser_bot.bots.main_bot.states import SchedulerState
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.schemas import SchedJob
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "sched"))
async def scheduler_menu(query: CallbackQuery, state: FSMContext):
    jobs = get_user_job(query.from_user.id)
    builder = scheduler_keyboard_builder()
    builder = menu_navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack(),
        inline_buttons=builder.buttons,
    )
    if jobs:
        await main_bot.send_message(
            query.from_user.id,
            render_template(
                "scheduler.html",
                user=query.from_user,
                jobs=jobs,
                settings=get_app_settings(),
            ),
            reply_markup=builder.as_markup(),
        )
        with suppress(TelegramBadRequest):
            await query.message.delete()
    else:
        await query.answer("No Job found")
        await start_callback(query, state)


@router.callback_query(
    SchedulerCallback.filter(F.name == "job" and F.action == "add"),
    SchedulerState.add_job_process_input,
)
async def scheduler_add_job_trigger_process(
    query: CallbackQuery, callback_data: SchedulerCallback, state: FSMContext
):
    state_data = await state.get_data()
    builder = menu_navigation_keyboard_builder(
        back_callback=CategoryCallback(name="sched-job", **state_data).pack(),
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
    await state.update_data(prev_message_id=message.message_id)
    await state.set_state(SchedulerState.add_job)


@router.message(SchedulerState.add_job)
async def scheduler_add_job_process(message: Message, state: FSMContext):
    state_data = await state.get_data()
    sched_jobs: list[SchedJob] = [SchedJob(**x) for x in state_data.get("sched_jobs")]
    for sched_job in sched_jobs:
        try:
            cron_trigger = CronTrigger(jitter=120).from_crontab(
                message.text, timezone=get_app_settings().TIMEZONE
            )
            sched_job.func = sched_job.func
            sched_job.trigger = cron_trigger
            sched_job_data: dict = sched_job.dict(exclude_none=True)
            sched_job_data.update({"id": f"{sched_job.id}:{sched_job.name}"})
            async_scheduler.add_job(**sched_job_data)
            await start_message(message, state)
        except Exception as e:
            message_answer = await message.answer(
                f"Error <code>{html.escape(e.args[0])}</code>. Try again"
            )
            await asyncio.sleep(3)
            await main_bot.delete_message(
                message.from_user.id, message_answer.message_id
            )
            if get_app_settings().LOGGING_LEVEL == "DEBUG":
                raise e
            return None


@router.callback_query(SchedulerCallback.filter(F.action == "rm"))
async def scheduler_remove_job_process(query: CallbackQuery, state: FSMContext):
    await query.answer(f"Enter a job ID e.g `aaa` or `aaa,bbb,ccc`")
    await state.set_state(SchedulerState.remove_job)
    await state.update_data(prev_message_id=query.message.message_id)


@router.message(SchedulerState.remove_job)
async def scheduler_remove_job_confirm(message: Message, state: FSMContext):
    state_data = await state.get_data()
    job_id: str | list[str] = message.text.strip(" ").split(",")
    await state.update_data(job_id=job_id)
    await main_bot.delete_message(
        message.from_user.id, state_data.get("prev_message_id")
    )
    builder = confirm_keyboard_builder()
    await message.reply(
        "Confirm removing",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(
    ConfirmCallback.filter(F.name == "rmjob"), SchedulerState.remove_job
)
async def scheduler_remove_job(
    query: CallbackQuery, callback_data: ConfirmCallback, state: FSMContext
):
    state_data = await state.get_data()
    job_id: str | list[str] = state_data.get("job_id")
    if callback_data.answer == "yes":
        results = remove_job(query.from_user.id, job_id)
        await query.answer("\n".join(results))
    elif callback_data.answer == "no":
        await query.answer("Deletion canceled")
    await state.clear()
    await scheduler_menu(query, state)
