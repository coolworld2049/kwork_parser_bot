from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import User, Message, CallbackQuery

from kwork_parser_bot.bots.main_bot.callbacks import MenuCallback
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.db.models.bot_user import BotUser
from kwork_parser_bot.db.session import get_db
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


async def start_cmd(user: User, state: FSMContext, message_id: int):
    with suppress(TelegramBadRequest):
        await main_bot.delete_message(user.id, message_id - 1)
    await state.clear()
    async with get_db() as db:
        db.add(BotUser(**user.dict(exclude_none=True)), _warn=False)
    await main_bot.send_message(
        user.id,
        render_template(
            "start.html",
            user=user,
            bot=await main_bot.me(),
        ),
        reply_markup=menu_keyboard_builder().as_markup(),
    )


@router.message(Command("start"))
async def start_message(message: Message, state: FSMContext):
    await start_cmd(message.from_user, state, message.message_id)


@router.callback_query(MenuCallback.filter(F.name == "start"))
async def start_callback(
    query: CallbackQuery,
    state: FSMContext,
):
    with suppress(TelegramBadRequest):
        await query.message.delete()
    await start_cmd(query.from_user, state, query.message.message_id)


@router.callback_query(MenuCallback.filter(F.name == "help"))
async def help_callback(query: CallbackQuery, state: FSMContext):
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
