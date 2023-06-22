from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from kwork_parser_bot.bots.main_bot.callbacks import (
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_keyboard_builder,
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
async def start_callback(query: CallbackQuery, state: FSMContext):
    with suppress(TelegramBadRequest):
        await query.message.delete()
        await main_bot.delete_message(query.from_user.id, query.message.message_id - 1)
    await state.clear()
    await main_bot.send_message(
        query.from_user.id,
        render_template(
            "start.html",
            user=query.from_user,
            settings=get_app_settings(),
        ),
        reply_markup=menu_keyboard_builder().as_markup(),
    )
