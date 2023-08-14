from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from prisma.models import KworkAccount

from kwork_api.kwork import get_kwork_api
from loader import bot
from telegram_bot.callbacks import (
    MenuCallback,
)
from telegram_bot.keyboards.kwork import (
    kwork_menu_keyboard_builder,
)
from telegram_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from telegram_bot.states import SchedulerState
from template_engine import render_template

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "client"))
async def kwork_menu(query: CallbackQuery, state: FSMContext):
    kwork_account = await KworkAccount.prisma().find_unique(
        where={"telegram_user_id": query.from_user.id}
    )
    actor = None
    if kwork_account:
        async with get_kwork_api(**kwork_account.dict()) as api:
            actor = await api.get_me()
    else:
        await query.answer("Log in to your kwork account", show_alert=True)
    builder = kwork_menu_keyboard_builder()
    builder = menu_navigation_keyboard_builder(
        builder,
        menu_callback=MenuCallback(name="start").pack(),
    )
    await bot.send_message(
        query.from_user.id,
        render_template("kwork_menu.html", actor=actor),
        reply_markup=builder.as_markup(),
    )
    with suppress(TelegramBadRequest):
        await query.message.delete()
    await state.set_state(SchedulerState.add_job_process_input)
