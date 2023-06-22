from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from kwork_parser_bot.bots.main_bot.callbacks import (
    MenuCallback,
    CategoryCallback,
)
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_keyboard_builder,
    navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.message(Command("start"))
async def start_message(message: Message, state: FSMContext):
    with suppress(TelegramBadRequest):
        await main_bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.clear()
    await message.answer(
        render_template(
            "start.html",
            user=message.from_user,
            settings=get_app_settings(),
        ),
        reply_markup=menu_keyboard_builder().as_markup(),
    )


@router.callback_query(MenuCallback.filter(F.name == "start"))
async def start_callback(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    with suppress(TelegramBadRequest):
        await main_bot.delete_message(query.from_user.id, query.message.message_id - 1)
    await state.clear()
    await query.message.delete()
    await main_bot.send_message(
        query.from_user.id,
        render_template(
            "start.html",
            user=query.from_user,
            settings=get_app_settings(),
        ),
        reply_markup=menu_keyboard_builder().as_markup(),
    )


@router.callback_query(MenuCallback.filter(F.name == "help"))
async def help_callback(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    await query.message.delete()
    commands = {x.command: x.description for x in get_app_settings().BOT_COMMANDS}
    builder = navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        query.from_user.id,
        render_template(
            "help.html",
            bot_commands=commands,
            settings=get_app_settings(),
        ),
        reply_markup=builder.as_markup(),
    )


# @router.message(Command("help"))
# async def help(message: Message):
#     commands = {x.command: x.description for x in get_app_settings().BOT_COMMANDS}
#     builder = navigation_keyboard_builder(
#         menu_callback=MenuCallback(name="start").pack(),
#     )
#     await message.answer(
#         render_template(
#             "help.html",
#             bot_commands=commands,
#             settings=get_app_settings(),
#         ),
#         reply_markup=builder.as_markup(),
#     )


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    _state = await state.get_state()
    await state.clear()
    await message.reply(f"{_state if _state else ''} canceled")
