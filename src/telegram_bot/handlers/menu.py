from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import User, Message, CallbackQuery

from telegram_bot.callbacks import MenuCallback
from telegram_bot.keyboards.menu import (
    menu_keyboard_builder,
)
from telegram_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from telegram_bot.loader import bot
from template_engine import render_template
from settings import settings

router = Router(name=__file__)


async def start_cmd(user: User, state: FSMContext, message_id: int):
    with suppress(TelegramBadRequest):
        await bot.delete_message(user.id, message_id - 1)
    await state.clear()
    await bot.send_message(
        user.id,
        render_template(
            "start.html",
            user=user,
            bot=await bot.me(),
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
    commands = {x.command: x.description for x in settings().BOT_COMMANDS}
    builder = menu_navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack()
    )
    await bot.send_message(
        query.from_user.id,
        render_template(
            "help.html",
            user=query.from_user,
            settings=settings(),
        ),
        reply_markup=builder.as_markup(),
    )
