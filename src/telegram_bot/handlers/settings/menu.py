from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from prisma import Json
from prisma.models import BotUser

from loader import bot
from telegram_bot.callbacks import MenuCallback, SettingsCallback
from telegram_bot.handlers.decorators import message_process_error
from telegram_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from telegram_bot.keyboards.settings import settings_menu_keyboard_builder
from telegram_bot.states import SettingsState
from template_engine import render_template

router = Router(name=__file__)


async def settings_menu(user: User):
    builder = settings_menu_keyboard_builder()
    builder = menu_navigation_keyboard_builder(
        builder=builder,
        menu_callback=MenuCallback(name="start").pack(),
    )
    bot_user = await BotUser.prisma().find_unique(where={"id": user.id})
    await bot.send_message(
        user.id,
        render_template("settings.html", settings=bot_user.settings),
        reply_markup=builder.as_markup(),
    )


@router.callback_query(MenuCallback.filter(F.name == "settings"))
async def settings_menu_callback(query: CallbackQuery, state: FSMContext):
    await settings_menu(query.from_user)
    with suppress(TelegramBadRequest):
        await query.message.delete()


@router.callback_query(
    SettingsCallback.filter(F.name == "settings" and F.action == "edit")
)
async def settings_edit(query: CallbackQuery, state: FSMContext):
    await query.answer("Enter new value e.g `key: value`")
    await state.set_state(SettingsState.edit)


@router.message(SettingsState.edit)
@message_process_error
async def settings_edit_message(message: Message, state: FSMContext):
    item = message.text.split(": ")
    bot_user = await BotUser.prisma().find_unique(where={"id": message.from_user.id})
    bot_user.settings.update({item[0]: item[1]})
    bot_user = await BotUser.prisma().update(
        data={"settings": Json(bot_user.settings)}, where={"id": message.from_user.id}
    )
    with suppress(TelegramBadRequest):
        await bot.delete_message(message.from_user.id, message.message_id - 1)
        await message.delete()
    await settings_menu(message.from_user)
