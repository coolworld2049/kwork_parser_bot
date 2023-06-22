from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from kwork_parser_bot.bots.main_bot.callbacks import SchedulerCallback


def scheduler_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="👀 Get jobs",
            callback_data=SchedulerCallback(action="get").pack(),
        ),
    )
    return builder
