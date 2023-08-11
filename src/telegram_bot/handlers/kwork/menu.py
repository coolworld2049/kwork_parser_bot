from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aredis_om import NotFoundError
from loguru import logger

from telegram_bot.callbacks import (
    MenuCallback,
)
from telegram_bot.keyboards.kwork import (
    kwork_menu_keyboard_builder,
)
from telegram_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from telegram_bot.loader import bot
from telegram_bot.states import SchedulerState
from kwork_api.client.exceptions import KworkException
from kwork_api.kwork import KworkApi
from kwork_api.models import KworkActor, KworkAccount
from template_engine import render_template

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "client"))
async def kwork_menu(query: CallbackQuery, state: FSMContext, kwork_api: KworkApi):
    try:
        kwork_account: KworkAccount = await kwork_api.kwork_account.find(
            KworkAccount.telegram_user_id == query.from_user.id
        ).first()
        if not kwork_account.actor:
            try:
                kwork_me = await kwork_api.get_me()
                actor = KworkActor(**kwork_me.dict(exclude_none=True))
                await kwork_account.update(actor=actor)
            except KworkException as ke:
                logger.error(ke)
    except* (Exception, NotFoundError) as e:
        kwork_account = KworkAccount(telegram_user_id=query.from_user.id)
    if not kwork_api:
        await query.answer("Log in to your kwork account", show_alert=True)
    builder = kwork_menu_keyboard_builder()
    builder = menu_navigation_keyboard_builder(
        builder,
        menu_callback=MenuCallback(name="start").pack(),
    )
    await bot.send_message(
        query.from_user.id,
        render_template("kwork_menu.html", actor=kwork_account.actor),
        reply_markup=builder.as_markup(),
    )
    with suppress(TelegramBadRequest):
        await query.message.delete()
    await state.set_state(SchedulerState.add_job_process_input)
