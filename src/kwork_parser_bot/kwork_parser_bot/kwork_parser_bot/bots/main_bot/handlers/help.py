from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from kwork_parser_bot.bots.main_bot.callbacks import MenuCallback, CategoryCallback
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "help"))
async def help_callback(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    with suppress(TelegramBadRequest):
        await query.message.delete()
    commands = {x.command: x.description for x in get_app_settings().BOT_COMMANDS}
    builder = menu_navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack()
    )
    await main_bot.send_message(
        query.from_user.id,
        render_template(
            "help.html",
            user=query.from_user,
            bot_commands=commands,
            settings=get_app_settings(),
        ),
        reply_markup=builder.as_markup(),
    )
