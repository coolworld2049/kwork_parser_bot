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
from kwork_parser_bot.bots.main_bot.thirdparty.kwork.main import get_my_account
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.message(Command("start"))
async def start_message(message: Message, state: FSMContext):
    with suppress(TelegramBadRequest):
        await main_bot.delete_message(message.from_user.id, message.message_id - 1)
    await state.clear()
    kwork_account = await get_my_account(message.from_user.id)
    bot_me = await main_bot.me()
    await message.answer(
        render_template(
            "start.html",
            user=message.from_user,
            kwork_account=kwork_account if kwork_account else {},
            bot=bot_me,
        ),
        reply_markup=menu_keyboard_builder().as_markup(),
    )


@router.callback_query(MenuCallback.filter(F.name == "start"))
async def start_callback(query: CallbackQuery, state: FSMContext):
    with suppress(TelegramBadRequest):
        await query.message.delete()
        await main_bot.delete_message(query.from_user.id, query.message.message_id - 1)
    await state.clear()
    kwork_account = await get_my_account(query.from_user.id)
    bot_me = await main_bot.me()
    await main_bot.send_message(
        query.from_user.id,
        render_template(
            "start.html",
            user=query.from_user,
            kwork_account=kwork_account,
            bot=bot_me,
        ),
        reply_markup=menu_keyboard_builder().as_markup(),
    )
