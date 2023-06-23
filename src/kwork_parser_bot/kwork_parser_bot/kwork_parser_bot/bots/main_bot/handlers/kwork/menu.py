from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from kwork_parser_bot.bots.main_bot.callbacks import (
    SchedulerCallback,
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.keyboards.kwork import (
    kwork_menu_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.scheduler import (
    scheduler_jobs_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.states import SchedulerState
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.schemas.kwork.schedjob import SchedJob
from kwork_parser_bot.services.kwork.base_class import KworkApi

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "kwork"))
async def kwork_menu(query: CallbackQuery, state: FSMContext, kwork_api: KworkApi):
    sched_jobs = [
        SchedJob(
            text="🔔 Receive account notifications",
            callback=SchedulerCallback(
                name="job",
                action="add",
                user_id=query.from_user.id,
            ),
            name="account",
            func=f"{get_app_settings().SCHED_JOBS_MODULE}:notify_about_kwork_notifications",
            args=(
                kwork_api.kwork_creds_dict(),
                query.from_user.id,
                query.from_user.id,
            ),
        )
    ]
    builder = kwork_menu_keyboard_builder()
    builder_sched_jobs = scheduler_jobs_keyboard_builder(sched_jobs)
    builder.add(*list(builder_sched_jobs.buttons))
    builder.adjust(1)
    builder = menu_navigation_keyboard_builder(
        builder, menu_callback=MenuCallback(name="start").pack()
    )
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Kwork Menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.update_data(sched_jobs=[x.dict() for x in sched_jobs])
    await state.set_state(SchedulerState.add_job_process_input)
    await query.message.delete()
