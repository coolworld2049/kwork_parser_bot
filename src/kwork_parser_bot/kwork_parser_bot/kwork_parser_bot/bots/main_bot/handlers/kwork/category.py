from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger
from redis.asyncio import ConnectionPool

from kwork_parser_bot.bots.main_bot.callbacks import (
    MenuCallback,
    KworkCategoryCallback,
    SchedulerCallback,
)
from kwork_parser_bot.bots.main_bot.keyboards.kwork import category_keyboard_builder
from kwork_parser_bot.bots.main_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.scheduler import (
    scheduler_jobs_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.states import SchedulerState
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.schemas.kwork.schedjob import SchedJob
from kwork_parser_bot.services.kwork.main import KworkApi

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "category"))
async def category_menu(
    query: CallbackQuery,
    callback_data: KworkCategoryCallback,
    state: FSMContext,
    kwork_api: KworkApi,
    redis_pool: ConnectionPool,
):
    await state.clear()
    if not kwork_api:
        await query.answer("Bad kwork credentials")
        return None
    category = await kwork_api.cached_category()
    builder = category_keyboard_builder(category, callback_name="subcategory")
    builder = menu_navigation_keyboard_builder(
        builder,
        back_callback=MenuCallback(name="kwork").pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Category 🤖",
        reply_markup=builder.as_markup(),
    )
    await query.message.delete()


@router.callback_query(KworkCategoryCallback.filter(F.name == "subcategory"))
async def subcategory(
    query: CallbackQuery,
    callback_data: KworkCategoryCallback,
    state: FSMContext,
    kwork_api: KworkApi,
    redis_pool: ConnectionPool,
):
    category = await kwork_api.cached_category()
    builder = category_keyboard_builder(
        category, callback_data.category_id, callback_name="scheduler-job"
    )
    builder = menu_navigation_keyboard_builder(
        builder,
        back_callback=MenuCallback(name="category", action="get").pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Subcategory 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.update_data(category_id=callback_data.category_id)
    await query.message.delete()


@router.callback_query(KworkCategoryCallback.filter(F.name == "scheduler-job"))
async def subcategory_sched_job(
    query: CallbackQuery,
    callback_data: KworkCategoryCallback,
    state: FSMContext,
    kwork_api: KworkApi,
    redis_pool: ConnectionPool,
):
    state_data = await state.get_data()
    category_id: int = state_data.get("category_id")
    subcategory_id: int = callback_data.subcategory_id
    if not all([category_id, subcategory_id]):
        logger.debug(all([category_id, subcategory_id]))
        return None
    category = await kwork_api.cached_category()
    parent_category = kwork_api.get_parent_category(category, category_id)
    category = kwork_api.get_category(category, parent_category.id, subcategory_id)

    notify_about_new_projects_callback = SchedulerCallback(
        name="job",
        action="add",
        category_id=category_id,
        subcategory_id=subcategory_id,
        user_id=query.from_user.id,
        from_="category",
    )
    sched_jobs = [
        SchedJob(
            text="🆕 Notify about new projects",
            callback=notify_about_new_projects_callback,
            name=f"{parent_category.name}-{category.name}",
            func=f"{get_app_settings().SCHED_JOBS_MODULE}:notify_about_new_projects",
            args=(
                kwork_api.creds,
                query.from_user.id,
                get_app_settings().NOTIFICATION_CHANNEL_ID
                if get_app_settings().NOTIFICATION_CHANNEL_ID
                else query.from_user.id,
                [category_id],
                notify_about_new_projects_callback.pack(),
            ),
        )
    ]
    builder = scheduler_jobs_keyboard_builder(sched_jobs)
    builder = menu_navigation_keyboard_builder(
        builder,
        back_callback=KworkCategoryCallback(
            name="subcategory",
            category_id=category_id,
            subcategory_id=subcategory_id,
        ).pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Scheduler jobs menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.update_data(
        sched_jobs=[x.dict() for x in sched_jobs], subcategory_id=subcategory_id
    )
    await state.set_state(SchedulerState.add_job_process_input)
    await query.message.delete()
