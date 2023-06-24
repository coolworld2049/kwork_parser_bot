from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from kwork_parser_bot.bots.main_bot.callbacks import MenuCallback
from kwork_parser_bot.bots.main_bot.handlers.menu import start_callback
from kwork_parser_bot.bots.main_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.scheduler import (
    scheduler_menu_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.services.kwork.base_class import KworkApi
from kwork_parser_bot.services.scheduler.lifetime import scheduler
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "scheduler"))
async def scheduler_menu(query: CallbackQuery, state: FSMContext, kwork_api: KworkApi):
    jobs = scheduler.get_user_job(query.from_user.id)
    builder = scheduler_menu_keyboard_builder()
    builder = menu_navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack(),
        inline_buttons=builder.buttons,
    )
    if jobs:
        await main_bot.send_message(
            query.from_user.id,
            render_template(
                "scheduler.html",
                user=query.from_user,
                jobs=jobs,
                settings=get_app_settings(),
            ),
            reply_markup=builder.as_markup(),
        )
        with suppress(TelegramBadRequest):
            await query.message.delete()
    else:
        await query.answer("No Job found")
        await start_callback(query, state, kwork_api)
