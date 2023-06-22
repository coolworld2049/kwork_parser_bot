from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from kwork_parser_bot.bots.main_bot.callbacks import ConfirmCallback


def confirm_keyboard_builder(name: str = "rmjob"):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="✔️",
            callback_data=ConfirmCallback(
                name=name,
                answer="yes",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="❌",
            callback_data=ConfirmCallback(
                name=name,
                answer="no",
            ).pack(),
        ),
    )
    return builder
