from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from kwork_parser_bot.bots.main_bot.callbacks.all import MenuCallback


def menu_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="👨‍💻 Kwork",
            callback_data=MenuCallback(
                name="kwork",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="📅 Scheduler",
            callback_data=MenuCallback(
                name="sched",
            ).pack(),
        ),
    )
    return builder
