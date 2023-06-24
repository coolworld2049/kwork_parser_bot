from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from kwork_parser_bot.bots.main_bot.callbacks import MenuCallback


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
                name="scheduler",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="📄 Help",
            callback_data=MenuCallback(
                name="help",
            ).pack(),
        ),
    )
    builder.adjust(2, 2)
    return builder
