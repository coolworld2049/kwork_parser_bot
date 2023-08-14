from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.callbacks import SchedulerCallback, ConfirmCallback
from telegram_bot.handlers.scheduler.menu import scheduler_menu
from telegram_bot.keyboards.confirm import confirm_keyboard_builder
from loader import bot, scheduler
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
async def scheduler_remove_job_confirm(message: Message, state: FSMContext):
    state_data = await state.get_data()
    job_id: str | list[str] = message.text.strip(" ").split(",")
    await state.update_data(job_id=job_id)
    await bot.delete_message(message.from_user.id, state_data.get("prev_message_id"))
    builder = confirm_keyboard_builder(callback_name="rmjob")
    await message.reply(
        "Confirm removing",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(
    ConfirmCallback.filter(F.name == "rmjob"), SchedulerState.remove_job
)
async def scheduler_remove_job(
    query: CallbackQuery,
    callback_data: ConfirmCallback,
    state: FSMContext,
):
    state_data = await state.get_data()
    job_id: str | list[str] = state_data.get("job_id")
    if callback_data.answer == "yes":
        results = scheduler.remove_user_job(query.from_user.id, job_id)
        await query.answer("\n".join(results), show_alert=True)
    elif callback_data.answer == "no":
        await query.answer("Deletion canceled")
    await state.clear()
    await scheduler_menu(query, state)
