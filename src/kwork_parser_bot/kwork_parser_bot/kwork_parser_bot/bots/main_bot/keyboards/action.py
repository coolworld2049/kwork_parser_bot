from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from kwork_parser_bot.schemas.action import Action


def action_keyboard_builder(
    actions: list[Action],
):
    builder = InlineKeyboardBuilder()
    for action in actions:
        builder.add(
            InlineKeyboardButton(
                text=action.text,
                callback_data=action.callback.pack(),
            )
        )
    return builder
