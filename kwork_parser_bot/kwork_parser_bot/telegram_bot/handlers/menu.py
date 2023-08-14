from contextlib import suppress

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import User, Message, CallbackQuery
from prisma import Json
from prisma.models import BotUser
from prisma.types import BotUserCreateInput, BotUserUpsertInput, BotUserUpdateInput

from loader import bot
from settings import get_settings
from telegram_bot.callbacks import MenuCallback
from telegram_bot.keyboards.menu import (
    menu_keyboard_builder,
)
from telegram_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from template_engine import render_template

router = Router(name=__file__)


async def start_cmd(user: User, state: FSMContext, message_id: int):
    with suppress(TelegramBadRequest):
        await bot.delete_message(user.id, message_id - 1)
    bot_user_update = BotUserUpdateInput(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )
    bot_user_create = BotUserCreateInput(
        id=user.id,
        settings=Json(data={"timezone": get_settings().TZ}),
        **bot_user_update
    )
    bot_user_upsert = BotUserUpsertInput(create=bot_user_create, update=bot_user_update)
    bot_user = await BotUser.prisma().upsert(
        where={"id": user.id}, data=bot_user_upsert
    )
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


@router.message(Command("help"))
async def help_message(message: Message, state: FSMContext):
    commands = {x.command: x.description for x in get_settings().BOT_COMMANDS}
    builder = menu_navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack()
    )
    await bot.send_message(
        message.from_user.id,
        render_template(
            "help.html",
            user=message.from_user,
            settings=get_settings(),
        ),
        reply_markup=builder.as_markup(),
    )
