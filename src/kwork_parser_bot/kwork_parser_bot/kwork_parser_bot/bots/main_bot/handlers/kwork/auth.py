import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from sqlalchemy import update

from kwork_parser_bot.bots.main_bot.callbacks import (
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.handlers.utils import message_process
from kwork_parser_bot.bots.main_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.states import KworkAuthState
from kwork_parser_bot.db.models.kwork_account import KworkAccount
from kwork_parser_bot.db.session import get_db
from kwork_parser_bot.services.kwork.base_class import KworkCreds, KworkApi
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


async def auth_menu(user: User, state: FSMContext):
    await state.clear()
    builder = menu_navigation_keyboard_builder(
        back_callback=MenuCallback(name="kwork").pack(),
    )
    message = await main_bot.send_message(
        user.id,
        render_template(
            "kwork_login.html",
        ),
        reply_markup=builder.as_markup(),
    )
    await state.set_state(KworkAuthState.set_creds)


@router.callback_query(MenuCallback.filter(F.name == "kwork-login"))
async def auth_callback(query: CallbackQuery, state: FSMContext):
    await auth_menu(query.from_user, state)
    await query.message.delete()


@router.message(KworkAuthState.start)
async def auth_message(message: Message, state: FSMContext):
    await auth_menu(message.from_user, state)


@router.callback_query(MenuCallback.filter(F.name == "kwork-logout"))
async def logout(query: CallbackQuery, state: FSMContext, kwork_api: KworkApi):
    await state.clear()
    await kwork_api.creds.delete_cache(query.from_user.id)
    await query.message.delete()


@router.message(KworkAuthState.set_creds)
@message_process
async def auth_creds(message: Message, state: FSMContext):
    def validate(v):
        if v and ":" in v and len(v.split(":")) == 2:
            v = v.split(":")
            return KworkCreds(login=v[0], password=v[1])
        else:
            raise ValueError("Incorrect format")

    creds = validate(message.text).dict()
    assert creds
    await state.update_data(creds=creds)
    builder = menu_navigation_keyboard_builder(
        back_callback=MenuCallback(name="kwork-login").pack(),
    )
    await message.answer(
        "Enter phone number from kwork account",
        reply_markup=builder.as_markup(),
    )
    await state.set_state(KworkAuthState.set_phone)


@router.message(KworkAuthState.set_phone)
@message_process
async def auth_phone(message: Message, state: FSMContext):
    state_data = await state.get_data()
    creds = KworkCreds(**state_data.get("creds"))

    def validate(v):
        regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
        if v and re.search(regex, v, re.I):
            creds.phone = message.text
            return creds
        else:
            raise ValueError("Phone Number Invalid")

    result = await KworkCreds.set_cache(
        message.from_user.id, validate(message.text).dict()
    )
    assert result
    kwork_account = KworkAccount(
        telegram_id=message.from_user.id,
        login=creds.login,
        password=KworkAccount.get_hashed_password(creds.password),
        phone=creds.phone,
    )
    try:
        async with get_db() as db:
            db.add(kwork_account)
    except:
        async with get_db() as db:
            stmt = (
                update(KworkAccount)
                .where(KworkAccount.telegram_id == message.from_user.id)
                .values(**kwork_account.to_dict())
            )
            await db.execute(stmt)
    await state.clear()
    await message.answer("Creds saved")
    await state.set_state(KworkAuthState.end)
