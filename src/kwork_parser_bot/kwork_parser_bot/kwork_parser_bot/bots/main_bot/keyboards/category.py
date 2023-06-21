from typing import Optional

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from kwork.types import Category
from kwork.types.category import Subcategory

from kwork_parser_bot.bots.main_bot.callbacks.all import CategoryCallback


def category_keyboard_builder(
    categories: list[Category | Subcategory],
    subcategory_id: Optional[int] = None,
    *,
    callback_name: Optional[str] = "category",
):
    builder = InlineKeyboardBuilder()
    if subcategory_id:
        selected_category: list[Category] = list(
            filter(lambda x: x.id == subcategory_id, categories)
        )
        if selected_category:
            selected_category: Category | None = selected_category.pop()
            categories = selected_category.subcategories
        else:
            return None
    for item in categories:
        builder.add(
            InlineKeyboardButton(
                text=item.name,
                callback_data=CategoryCallback(
                    name=callback_name,
                    category_id=item.id,
                ).pack(),
            )
        )
    return builder
