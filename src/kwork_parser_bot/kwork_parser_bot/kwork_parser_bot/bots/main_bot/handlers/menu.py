from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import User, Message, CallbackQuery

from kwork_parser_bot.bots.main_bot.callbacks import MenuCallback, KworkCategoryCallback
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_keyboard_builder,
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.services.kwork.base_class import KworkApi
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


async def start_cmd(
    user: User, state: FSMContext, message_id: int, kwork_api: KworkApi
):
    with suppress(TelegramBadRequest):
        await main_bot.delete_message(user.id, message_id - 1)
    await state.clear()
    kwork_account = await kwork_api.get_my_account(user.id)
    bot_me = await main_bot.me()
    await main_bot.send_message(
        user.id,
        render_template(
            "start.html",
            user=user,
            kwork_account=kwork_account if kwork_account else {},
            bot=bot_me,
        ),
        reply_markup=menu_keyboard_builder().as_markup(),
    )


@router.message(Command("start"))
async def start_message(message: Message, state: FSMContext, kwork_api: KworkApi):
    await start_cmd(message.from_user, state, message.message_id, kwork_api)


@router.callback_query(MenuCallback.filter(F.name == "start"))
async def start_callback(
    query: CallbackQuery,
    state: FSMContext,
    kwork_api: KworkApi,
):
    with suppress(TelegramBadRequest):
        await query.message.delete()
    await start_cmd(query.from_user, state, query.message.message_id, kwork_api)


@router.callback_query(MenuCallback.filter(F.name == "help"))
async def help_callback(
    query: CallbackQuery, callback_data: KworkCategoryCallback, state: FSMContext
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
