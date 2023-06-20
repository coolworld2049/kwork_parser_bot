from typing import Optional

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from kwork.types import Category
from kwork.types.category import Subcategory

from kwork_parser_bot.bots.main_bot.callbacks.order_exchange import CategoryCallback


def category_keyboard_builder(categories: list[Category | Subcategory], selected_category_id: Optional[int] = None):
    builder = InlineKeyboardBuilder()
    if selected_category_id:
        selected_category: Category = list(filter(lambda x: x.id == selected_category_id, categories)).pop()
        categories = selected_category.subcategories
    for item in categories:
        builder.add(
            InlineKeyboardButton(
                text=item.name,
                callback_data=CategoryCallback(category_id=item.id, selected_category_id=selected_category_id).pack(),
            )
        )
    return builder
