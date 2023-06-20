from typing import Optional

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

from kwork_parser_bot.bots.main_bot.callbacks.base import SubcategoryActionCallback
from kwork_parser_bot.schemas.action import Action


def action_keyboard_builder(
    actions: list[Action],
    category_id: int,
    subcategory_id: int,
    *,
    callback_name: Optional[str] = "action",
):
    builder = InlineKeyboardBuilder()
    for action in actions:
        logger.debug(InlineKeyboardButton(
                text=action.text,
                callback_data=SubcategoryActionCallback(
                    name=callback_name,
                    category_id=category_id,
                    subcategory_id=subcategory_id,
                    action=action.action
                ).pack()
        ))
        builder.add(
            InlineKeyboardButton(
                text=action.text,
                callback_data=SubcategoryActionCallback(
                    name=callback_name,
                    category_id=category_id,
                    subcategory_id=subcategory_id,
                    action=action.action
                ).pack(),
            )
        )
    return builder
