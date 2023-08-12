from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from telegram_bot.callbacks import MenuCallback
from telegram_bot.handlers.menu import start_callback
from telegram_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from telegram_bot.keyboards.scheduler import (
    scheduler_menu_keyboard_builder,
)
from telegram_bot.loader import bot, scheduler
from settings import settings
from template_engine import render_template

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "scheduler"))
async def scheduler_menu(query: CallbackQuery, state: FSMContext):
    jobs = scheduler.get_user_job(query.from_user.id)
    builder = scheduler_menu_keyboard_builder()
    builder = menu_navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack(),
        inline_buttons=builder.buttons,
    )
    if jobs:
        await bot.send_message(
            query.from_user.id,
            render_template(
                "scheduler.html",
                user=query.from_user,
                jobs=jobs,
                settings=settings(),
            ),
            reply_markup=builder.as_markup(),
        )
        with suppress(TelegramBadRequest):
            await query.message.delete()
    else:
        await query.answer("Not found jobs")
        await start_callback(query, state)
