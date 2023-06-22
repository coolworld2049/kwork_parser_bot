from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from kwork_parser_bot.bots.main_bot.callbacks import SchedulerCallback


def scheduler_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🗑️ Remove",
            callback_data=SchedulerCallback(action="rm").pack(),
        )
    )
    return builder
