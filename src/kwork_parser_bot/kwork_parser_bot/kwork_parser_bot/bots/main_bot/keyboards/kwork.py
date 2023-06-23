from typing import Optional

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from kwork.types import Category
from kwork.types.category import Subcategory

from kwork_parser_bot.bots.main_bot.callbacks import KworkCategoryCallback, MenuCallback


def kwork_menu_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🔎 Categories",
            callback_data=MenuCallback(name="category").pack(),
        ),
    )
    return builder


def category_keyboard_builder(
    categories: list[Category | Subcategory],
    category_id: Optional[int] = None,
    *,
    callback_name: Optional[str] = "category",
):
    builder = InlineKeyboardBuilder()
    if isinstance(categories[0], Category) and category_id:
        selected_category = list(filter(lambda x: x.id == category_id, categories))
        if not selected_category:
            return None
        selected_category = selected_category.pop()
        categories = selected_category.subcategories

    def define_type_category(categories, _id):
        if isinstance(categories[0], Category):
            if category_id:
                _id = category_id
            return {"category_id": _id}
        elif isinstance(categories[0], Subcategory):
            return {"subcategory_id": _id}

    for item in categories:
        builder.add(
            InlineKeyboardButton(
                text=item.name,
                callback_data=KworkCategoryCallback(
                    name=callback_name, **define_type_category(categories, item.id)
                ).pack(),
            )
        )
    builder.adjust(1)
    return builder
