import re
from contextlib import suppress

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User, ReplyKeyboardRemove

from kwork_api.kwork import KworkApi, get_kwork_api
from kwork_api.models import KworkAccount
from telegram_bot.callbacks import (
    MenuCallback,
)
from telegram_bot.handlers.decorators import message_process_error
from telegram_bot.handlers.kwork.menu import kwork_menu
from telegram_bot.handlers.menu import start_message, start_callback
from telegram_bot.keyboards.kwork import auth_keyboard_builder
from telegram_bot.loader import bot
from telegram_bot.states import AuthState

router = Router(name=__file__)


async def auth_menu(user: User, state: FSMContext):
    await state.clear()
    message = await bot.send_message(
        user.id,
        "Enter your kwork account login.\n<b>Attention! Data will be updated</b>",
        reply_markup=auth_keyboard_builder(callback_name="client").as_markup(),
    )
    await state.update_data(
        first_message_id=message.message_id, current_message_id=message.message_id
    )
    await state.set_state(AuthState.set_login)


@router.callback_query(MenuCallback.filter(F.name == "client-login"))
async def auth_callback(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await auth_menu(query.from_user, state)


async def auth_cancel(user: User, state: FSMContext):
    state_data = await state.get_data()
    with suppress(TelegramBadRequest, TypeError):
        for m_id in range(
            state_data.get("first_message_id"), state_data.get("current_message_id") + 1
        ):
            await bot.delete_message(user.id, m_id)
    await state.clear()


@router.message(F.text == "❌")
async def auth_cancel_message(message: Message, state: FSMContext):
    await message.delete()
    await auth_cancel(message.from_user, state)
    await start_message(message, state)


@router.callback_query(
    MenuCallback.filter(F.name == "client-login" and F.action == "rm")
)
async def auth_cancel_callback(
    query: CallbackQuery, state: FSMContext, kwork_api: KworkApi
):
    await query.message.delete()
    await auth_cancel(query.from_user, state)
    await kwork_menu(query, state, kwork_api)


@router.message(AuthState.set_login)
@message_process_error
async def auth_password(message: Message, state: FSMContext):
    await state.update_data(login=message.text, current_message_id=message.message_id)
    builder = auth_keyboard_builder()
    await message.answer(
        "Enter password.", reply_markup=auth_keyboard_builder().as_markup()
    )
    await state.set_state(AuthState.set_password)


@router.message(AuthState.set_password)
@message_process_error
async def auth_phone(message: Message, state: FSMContext):
    await state.update_data(
        password=message.text, current_message_id=message.message_id
    )
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
    await state.set_state(AuthState.set_phone)


@router.message(AuthState.set_phone)
@router.message(F.contact, AuthState.set_phone)
@router.message(F.text == "❌", AuthState.set_phone)
@message_process_error
async def auth_finish(message: Message, state: FSMContext):
    await state.update_data(current_message_id=message.message_id)
    state_data = await state.get_data()
    phone = None
    if message.contact:
        phone = message.contact.phone_number
    elif message.text == "❌":
        await auth_cancel_message(message, state)
    else:
        regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
        if message.text and re.search(regex, message.text, re.I):
            phone = message.text
        else:
            raise ValueError("Phone Number Invalid")
    kwork_account = KworkAccount(
        telegram_user_id=message.from_user.id,
        login=state_data.get("login"),
        password=state_data.get("password"),
        phone=phone,
    )
    async with get_kwork_api(kwork_account) as api:
        await api.get_token()
    await kwork_account.save()
    await kwork_account.expire(86400 * 7)
    with suppress(TelegramBadRequest):
        for m_id in range(state_data.get("first_message_id"), message.message_id + 1):
            await bot.delete_message(message.from_user.id, m_id)
    message_answer = await message.answer("Saved", reply_markup=ReplyKeyboardRemove())
    await message_answer.delete()
    await start_message(message, state)


@router.callback_query(MenuCallback.filter(F.name == "client-logout"))
async def logout(query: CallbackQuery, state: FSMContext, kwork_api: KworkApi):
    if kwork_api:
        kwork_account = kwork_api.kwork_account
        await kwork_account.expire(0)
    await start_callback(query, state)
