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
            text="ℹ️ Help",
            callback_data=MenuCallback(
                name="help",
            ).pack(),
        ),
    )
    builder.adjust(2, 2)
    return builder


def menu_navigation_keyboard_builder(
    builder: InlineKeyboardBuilder = None,
    back_callback: str = None,
    menu_callback: str = None,
    inline_buttons: list[InlineKeyboardButton] = None,
):
    if not back_callback and not menu_callback:
        return None
    if not builder:
        builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text="👈 Back",
            callback_data=back_callback,
        )
        if back_callback
        else None,
        InlineKeyboardButton(
            text="👈 Menu",
            callback_data=menu_callback,
        )
        if menu_callback
        else None,
    ]
    buttons = list(filter(lambda x: x is not None, buttons))
    builder.row(*inline_buttons) if inline_buttons else None
    builder.row(*buttons, width=len(buttons) if len(buttons) <= 2 else 2)
    return builder
