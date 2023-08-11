from typing import Optional

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.callbacks import (
    KworkCategoryCallback,
    MenuCallback,
    BlacklistCallback,
)
from kwork_api.client.types import Category
from kwork_api.client.types.category import Subcategory


def kwork_menu_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔑 Login",
            callback_data=MenuCallback(
                name="client-login",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="🗑️ Logout",
            callback_data=MenuCallback(
                name="client-logout",
            ).pack(),
        ),
        width=2,
    )
    builder.row(
        InlineKeyboardButton(
            text="🔎 Category",
            callback_data=MenuCallback(name="category").pack(),
        ),
        InlineKeyboardButton(
            text="🚫 Blacklist",
            callback_data=MenuCallback(name="blacklist").pack(),
        ),
    )
    return builder


def auth_keyboard_builder(callback_name: str = "client-login"):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="❌",
            callback_data=MenuCallback(
                name=callback_name,
                action="rm",
            ).pack(),
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


def blacklist_menu_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="add",
            callback_data=BlacklistCallback(name="blacklist", action="add").pack(),
        ),
        InlineKeyboardButton(
            text="delete",
            callback_data=BlacklistCallback(name="blacklist", action="rm").pack(),
        ),
    )
    return builder
