from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from loguru import logger

from kwork_parser_bot.bots.main_bot.callbacks.all import (
    CategoryCallback,
    SchedulerCallback,
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.keyboards.navigation import (
    navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.scheduler import (
    scheduler_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import async_scheduler, main_bot
from kwork_parser_bot.bots.main_bot.states import SchedulerState
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "sched"))
async def scheduler(query: CallbackQuery, callback_data: CategoryCallback):
    await query.message.delete()
    scheduler_builder = scheduler_keyboard_builder()
    builder = navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack(),
        inline_buttons=scheduler_builder.buttons,
    )
    await main_bot.send_message(
        query.from_user.id,
        render_template(
            "scheduler_menu.html",
        ),
        reply_markup=builder.as_markup(),
    )


@router.callback_query(SchedulerCallback.filter(F.action == "get"))
async def scheduler_get(query: CallbackQuery, callback_data: CategoryCallback):
    jobs = async_scheduler.get_jobs()
    buttons = [
        InlineKeyboardButton(
            text="🗑️ Remove job",
            callback_data=SchedulerCallback(action="remove").pack(),
        )
    ]
    builder = navigation_keyboard_builder(
        back_callback=MenuCallback(name="sched").pack(),
        menu_callback=MenuCallback(name="start").pack(),
        inline_buttons=buttons,
    )
    if jobs:
        await main_bot.send_message(
            query.from_user.id,
            render_template(
                "scheduler_jobs.html",
                user=query.from_user,
                jobs=jobs,
                settings=get_app_settings(),
            ),
            reply_markup=builder.as_markup(),
        )
        await query.message.delete()
    else:
        await query.answer("No Job found")


@router.callback_query(SchedulerCallback.filter(F.action == "remove"))
async def scheduler_add_process_input(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    await query.answer(f"Enter a job ID or a list of job IDs separated by `,`")
    await state.set_state(SchedulerState.remove_job)
    await state.update_data(prev_message_id=query.message.message_id)


async def remove_job(job_id: str | list[str]):
    results = []
    if not isinstance(job_id, list):
        job_id = [job_id]
    for id in job_id:
        try:
            async_scheduler.remove_job(id)
        except Exception as e:
            logger.debug(e)
        if not async_scheduler.get_job(id):
            results.append(f"Successfully deleted {id}")
        else:
            results.append(f"Failed to delete {id}")
    return results


@router.message(SchedulerState.remove_job)
async def scheduler_delete_job_process(message: Message, state: FSMContext):
    job_id = message.text.strip(" ").split(",")
    state_data = await state.get_data()
    await main_bot.delete_message(
        message.from_user.id, state_data.get("prev_message_id")
    )
    builder = navigation_keyboard_builder(
        back_callback=MenuCallback(name="sched").pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    results = await remove_job(job_id)
    await message.reply(str(results), reply_markup=builder.as_markup())
    await state.clear()
