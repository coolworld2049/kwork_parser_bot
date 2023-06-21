from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from kwork_parser_bot.bots.main_bot.callbacks.all import SchedulerCallback


def scheduler_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="👀 Get jobs",
            callback_data=SchedulerCallback(
                action="get"
            ).pack(),
        ),
        InlineKeyboardButton(
            text="🗑️ Remove job",
            callback_data=SchedulerCallback(
                action="remove"
            ).pack(),
        )
    )
    return builder
