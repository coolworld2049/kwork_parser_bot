from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import ConfirmCallback


def confirm_keyboard_builder(callback_name: str):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="✔️",
            callback_data=ConfirmCallback(
                name=callback_name,
                answer="yes",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="❌",
            callback_data=ConfirmCallback(
                name=callback_name,
                answer="no",
            ).pack(),
        ),
    )
    return builder
