from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.callbacks import SettingsCallback


def settings_menu_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Edit",
            callback_data=SettingsCallback(name="settings", action="edit").pack(),
        )
    )
    return builder
