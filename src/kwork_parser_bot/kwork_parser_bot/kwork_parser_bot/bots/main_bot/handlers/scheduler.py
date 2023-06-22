from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from kwork_parser_bot.bots.main_bot.callbacks import (
    SchedulerCallback,
    MenuCallback,
    ConfirmCallback,
)
from kwork_parser_bot.bots.main_bot.handlers.start import start_callback
from kwork_parser_bot.bots.main_bot.keyboards.confirm import confirm_keyboard_builder
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.scheduler import (
    scheduler_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.sched.main import remove_job, get_user_job
from kwork_parser_bot.bots.main_bot.states import SchedulerState
from kwork_parser_bot.core.config import get_app_settings
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
