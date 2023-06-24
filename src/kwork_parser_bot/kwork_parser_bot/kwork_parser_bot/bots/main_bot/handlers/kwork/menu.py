from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from kwork_parser_bot.bots.main_bot.callbacks import (
    SchedulerCallback,
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.handlers.kwork.auth import auth_menu
from kwork_parser_bot.bots.main_bot.keyboards.kwork import (
    kwork_menu_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.scheduler import (
    scheduler_jobs_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.states import SchedulerState, KworkAuthState
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.schemas.kwork.schedjob import SchedJob
from kwork_parser_bot.services.kwork.base_class import KworkApi
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "kwork"))
async def kwork_menu(query: CallbackQuery, state: FSMContext, kwork_api: KworkApi):
    if not kwork_api:
        await state.set_state(KworkAuthState.set_login)
        await query.message.delete()
        await auth_menu(query.from_user, state)
        return None
    try:
        account = await kwork_api.my_account(query.from_user.id)
    except AttributeError as e:
        account = {}
    builder = kwork_menu_keyboard_builder()
    if kwork_api:
        sched_jobs = [
            SchedJob(
                text="🔔 Receive account notifications",
                callback=SchedulerCallback(
                    name="job", action="add", user_id=query.from_user.id, from_="kwork"
                ),
                name="account",
                func=f"{get_app_settings().SCHED_JOBS_MODULE}:notify_about_kwork_notifications",
                args=(
                    kwork_api.creds,
                    query.from_user.id,
                    query.from_user.id,
                ),
            )
        ]
        await state.update_data(sched_jobs=[x.dict() for x in sched_jobs])
        builder_sched_jobs = scheduler_jobs_keyboard_builder(sched_jobs)
        builder.add(*list(builder_sched_jobs.buttons))
        builder.adjust(2, 1, repeat=True)
    else:
        buttons = list(builder.buttons).copy()
        buttons.pop(1)
        builder = InlineKeyboardBuilder().add(*buttons)
        builder_sched_jobs = None
        await query.answer("Log in to your kwork account", show_alert=True)
    builder = menu_navigation_keyboard_builder(
        builder,
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        query.from_user.id,
        render_template("kwork_menu.html", account=account),
        reply_markup=builder.as_markup(),
    )
    await state.set_state(SchedulerState.add_job_process_input)
    await query.message.delete()
