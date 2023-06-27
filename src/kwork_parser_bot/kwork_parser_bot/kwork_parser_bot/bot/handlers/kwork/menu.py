from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from kwork_parser_bot.bot.callbacks import (
    SchedulerCallback,
    MenuCallback,
)
from kwork_parser_bot.bot.handlers.kwork.auth import auth_menu
from kwork_parser_bot.bot.keyboards.kwork import (
    kwork_menu_keyboard_builder,
)
from kwork_parser_bot.bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bot.keyboards.scheduler import (
    scheduler_jobs_keyboard_builder,
)
from kwork_parser_bot.bot.loader import main_bot
from kwork_parser_bot.bot.states import SchedulerState, AuthState
from kwork_parser_bot.services.kwork.kwork import KworkApi
from kwork_parser_bot.services.kwork.schemas import KworkActor, KworkAccount
from kwork_parser_bot.services.scheduler.schemas import SchedulerJob
from kwork_parser_bot.settings import settings
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "api"))
async def kwork_menu(query: CallbackQuery, state: FSMContext, kwork_api: KworkApi):
    if not kwork_api:
        await state.set_state(AuthState.set_login)
        await query.message.delete()
        await auth_menu(query.from_user, state)
        return None
    kwork_account: KworkAccount = await kwork_api.kwork_account.find(
        KworkAccount.telegram_user_id == query.from_user.id
    ).first()
    if not kwork_account.actor:
        kwork_me = await kwork_api.get_me()
        actor = KworkActor(**kwork_me.dict(exclude_none=True))
        await kwork_account.update(actor=actor)
    builder = kwork_menu_keyboard_builder()
    if kwork_api:
        sched_job = SchedulerJob(
            text="🔔 Receive notifications",
            callback=SchedulerCallback(
                name="job", action="add", user_id=query.from_user.id, from_="api"
            ),
            name="kwork_account",
            func=f"{settings().SCHED_JOBS_MODULE}:notify_about_kwork_notifications",
            args=(
                kwork_api.kwork_account,
                query.from_user.id,
                settings().NOTIFICATION_CHANNEL_ID
                if settings().NOTIFICATION_CHANNEL_ID
                else query.from_user.id,
            ),
        )
        await state.update_data(sched_job=sched_job.dict())
        builder_sched_jobs = scheduler_jobs_keyboard_builder(sched_job)
        builder.add(*list(builder_sched_jobs.buttons))
        builder.adjust(2, 1, repeat=True)
    else:
        buttons = list(builder.buttons).copy()
        buttons.pop(1)
        builder = InlineKeyboardBuilder().add(*buttons)
        await query.answer("Log in to your api kwork_account", show_alert=True)
    builder = menu_navigation_keyboard_builder(
        builder,
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        query.from_user.id,
        render_template("kwork_menu.html", actor=kwork_account.actor),
        reply_markup=builder.as_markup(),
    )
    await state.set_state(SchedulerState.add_job_process_input)
    await query.message.delete()
