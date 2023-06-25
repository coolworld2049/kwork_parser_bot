import re
from contextlib import suppress

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User, ReplyKeyboardRemove
from sqlalchemy import update

from kwork_parser_bot.bots.main_bot.callbacks import (
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.handlers.menu import start_message, start_callback
from kwork_parser_bot.bots.main_bot.handlers.utils import message_process
from kwork_parser_bot.bots.main_bot.keyboards.kwork import auth_keyboard_builder
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.states import KworkAuthState
from kwork_parser_bot.db.models.kwork_account import KworkAccount
from kwork_parser_bot.db.session import get_db
from kwork_parser_bot.schemas.pydantic_schema import PydanticKworkAccount
from kwork_parser_bot.services.kwork.main import KworkCreds, KworkApi
from kwork_parser_bot.services.kwork.lifetime import get_kwork_api

router = Router(name=__file__)


async def auth_menu(user: User, state: FSMContext):
    await state.clear()
    message = await main_bot.send_message(
        user.id,
        "Enter your kwork login.\n<b>Attention! Data will be updated</b>",
        reply_markup=auth_keyboard_builder().as_markup(),
    )
    await state.update_data(
        first_message_id=message.message_id, current_message_id=message.message_id
    )
    await state.set_state(KworkAuthState.set_login)


async def auth_cancel(user: User, state: FSMContext):
    state_data = await state.get_data()
    with suppress(TelegramBadRequest):
        for m_id in range(
            state_data.get("first_message_id"), state_data.get("current_message_id") + 1
        ):
            await main_bot.delete_message(user.id, m_id)
    await state.clear()


@router.message(F.text == "❌")
async def auth_cancel_message(message: Message, state: FSMContext):
    await message.delete()
    await auth_cancel(message.from_user, state)
    await start_message(message, state)


@router.callback_query(
    MenuCallback.filter(F.name == "kwork-login" and F.action == "rm")
)
async def auth_cancel_callback(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await auth_cancel(query.from_user, state)
    await start_callback(query, state)


@router.callback_query(MenuCallback.filter(F.name == "kwork-login"))
async def auth_callback(query: CallbackQuery, state: FSMContext):
    await auth_menu(query.from_user, state)
    await query.message.delete()


@router.message(KworkAuthState.start)
async def auth_message(message: Message, state: FSMContext):
    await auth_menu(message.from_user, state)


@router.message(KworkAuthState.set_login)
@message_process
async def auth_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text, current_message_id=message.message_id)
    builder = auth_keyboard_builder()
    await message.answer(
        "Enter password.", reply_markup=auth_keyboard_builder().as_markup()
    )
    await state.set_state(KworkAuthState.set_password)


@router.message(KworkAuthState.set_password)
@message_process
async def auth_password(message: Message, state: FSMContext):
    await state.update_data(
        password=message.text, current_message_id=message.message_id
    )
    state_data = await state.get_data()
    async with get_kwork_api(KworkCreds(**state_data)) as api:
        await api.get_token()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="📱 Send phone number", request_contact=True),
                types.KeyboardButton(text="❌"),
            ],
        ],
        resize_keyboard=True,
    )
    await message.answer("Enter phone number", reply_markup=keyboard)
    await state.set_state(KworkAuthState.set_phone)


@router.message(KworkAuthState.set_phone)
@router.message(F.contact, KworkAuthState.set_phone)
@router.message(F.text == "❌", KworkAuthState.set_phone)
@message_process
async def auth_phone(message: Message, state: FSMContext):
    await state.update_data(current_message_id=message.message_id)
    state_data = await state.get_data()
    creds = KworkCreds(**state_data)

    def process_phone_input(message, state, creds):
        regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
        if message.text and re.search(regex, message.text, re.I):
            creds.phone = message.text
        else:
            raise ValueError("Phone Number Invalid")

    if message.contact:
        creds.phone = message.contact.phone_number
    elif message.text == "❌":
        await auth_cancel_message(message, state)
    else:
        process_phone_input(message, state, creds)

    async def create_account(user: User, creds):
        kwork_account = PydanticKworkAccount(
            telegram_id=user.id,
            login=creds.login,
            password=KworkAccount.get_hashed_password(creds.password),
            phone=creds.phone,
        )
        async with get_db() as db:
            stmt = (
                update(KworkAccount)
                .where(KworkAccount.telegram_id == user.id)
                .values(**kwork_account.dict())
            )
            await db.execute(stmt)

    await state.update_data(creds=creds.dict())
    await creds.set_cache(message.from_user.id, creds.dict())
    await create_account(message.from_user, creds)

    with suppress(TelegramBadRequest):
        for m_id in range(state_data.get("first_message_id"), message.message_id + 1):
            await main_bot.delete_message(message.from_user.id, m_id)
    await state.clear()
    message_answer = await message.answer("Saved", reply_markup=ReplyKeyboardRemove())
    await message_answer.delete()
    await start_message(message, state)


@router.callback_query(MenuCallback.filter(F.name == "kwork-logout"))
async def logout(query: CallbackQuery, state: FSMContext, kwork_api: KworkApi):
    await state.clear()
    await kwork_api.creds.delete_cache(query.from_user.id)
    await start_callback(query, state)
