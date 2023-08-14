from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from loader import scheduler, bot
from telegram_bot.callbacks import SchedulerCallback
from telegram_bot.handlers.menu import start_cmd
from telegram_bot.handlers.scheduler.menu import scheduler_menu
from telegram_bot.states import SchedulerState

router = Router(name=__file__)


@router.callback_query(
    SchedulerCallback.filter(F.name == "job" and F.action == "rm"),
)
async def scheduler_remove_job_process(
    query: CallbackQuery, callback_data: SchedulerCallback, state: FSMContext
):
    await state.clear()
    await query.answer(f"Enter a job ID e.g `aaa` or `aaa,bbb,ccc`")
    await state.set_state(SchedulerState.remove_job)
    await state.update_data(prev_message_id=query.message.message_id)


@router.message(SchedulerState.remove_job)
async def scheduler_remove_job(message: Message, state: FSMContext):
    state_data = await state.get_data()
    job_id: str | list[str] = message.text.strip(" ").split(",")
    prev_message_id = state_data.get("prev_message_id")
    results = scheduler.remove_user_job(message.from_user.id, job_id)
    with suppress(TelegramBadRequest):
        await bot.delete_message(message.from_user.id, message.message_id)
        await bot.delete_message(message.from_user.id, message.message_id - 1)
    exist = await scheduler_menu(message.from_user, state)
    if not exist:
        await start_cmd(message.from_user, state, message.message_id)
