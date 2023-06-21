from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def navigation_keyboard_builder(
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
