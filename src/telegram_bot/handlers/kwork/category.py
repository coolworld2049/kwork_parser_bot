from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger
from prisma.models import KworkAccount

from kwork_api.kwork import get_kwork_api
from loader import bot, redis_pool
from scheduler.models import SchedulerJob
from settings import get_settings
from telegram_bot.callbacks import (
    MenuCallback,
    KworkCategoryCallback,
    SchedulerCallback,
)
from telegram_bot.keyboards.kwork import category_keyboard_builder
from telegram_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from telegram_bot.keyboards.scheduler import (
    scheduler_jobs_keyboard_builder,
)
from telegram_bot.states import SchedulerState

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "category"))
async def category_menu(
    query: CallbackQuery,
    callback_data: KworkCategoryCallback,
    state: FSMContext,
):
    await state.clear()
    kwork_account = await KworkAccount.prisma().find_unique(
        where={"telegram_user_id": query.from_user.id}
    )
    async with get_kwork_api(**kwork_account.dict()) as api:
        category = await api.cached_category(redis_pool)
    builder = category_keyboard_builder(category, callback_name="subcategory")
    builder = menu_navigation_keyboard_builder(
        builder,
        back_callback=MenuCallback(name="client").pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    await bot.send_message(
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
):
    kwork_account = await KworkAccount.prisma().find_unique(
        where={"telegram_user_id": query.from_user.id}
    )
    async with get_kwork_api(**kwork_account.dict()) as api:
        category = await api.cached_category(redis_pool)
    builder = category_keyboard_builder(
        category, callback_data.category_id, callback_name="scheduler-job"
    )
    builder = menu_navigation_keyboard_builder(
        builder,
        back_callback=MenuCallback(name="category", action="get").pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    await bot.send_message(
        query.from_user.id,
        text="🤖 Subcategory 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.set_data({"category_id": callback_data.category_id})
    await query.message.delete()


@router.callback_query(KworkCategoryCallback.filter(F.name == "scheduler-job"))
async def subcategory_sched_job(
    query: CallbackQuery,
    callback_data: KworkCategoryCallback,
    state: FSMContext,
):
    state_data = await state.get_data()
    category_id: int = state_data.get("category_id")
    subcategory_id: int = callback_data.subcategory_id
    if not all([category_id, subcategory_id]):
        logger.debug(all([category_id, subcategory_id]))
        return None
    kwork_account = await KworkAccount.prisma().find_unique(
        where={"telegram_user_id": query.from_user.id}
    )
    async with get_kwork_api(**kwork_account.dict()) as api:
        category = await api.cached_category(redis_pool)
        parent_category = api.get_parent_category(category, category_id)
        category = api.get_category(category, parent_category.id, subcategory_id)

    notify_about_new_projects_callback = SchedulerCallback(
        name="job",
        action="add",
        category_id=category_id,
        subcategory_id=subcategory_id,
        telegram_user_id=query.from_user.id,
        from_="category",
    )
    sched_job = SchedulerJob(
        text="🆕 Notify about new projects",
        callback=notify_about_new_projects_callback,
        name=f"{parent_category.name}-{category.name}",
        func=f"{get_settings().SCHED_JOBS_MODULE}:notify_about_new_projects",
        args=(
            query.from_user.id,
            get_settings().NOTIFICATION_CHANNEL_ID
            if get_settings().NOTIFICATION_CHANNEL_ID
            else query.from_user.id,
            [subcategory_id],
            notify_about_new_projects_callback.pack(),
        ),
    )
    builder = scheduler_jobs_keyboard_builder(sched_job)
    builder = menu_navigation_keyboard_builder(
        builder,
        back_callback=KworkCategoryCallback(
            name="subcategory",
            category_id=category_id,
            subcategory_id=subcategory_id,
        ).pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    await bot.send_message(
        query.from_user.id,
        text="🤖 Scheduler jobs menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.update_data(sched_job=sched_job.dict(), subcategory_id=subcategory_id)
    await state.set_state(SchedulerState.add_job_process_input)
    await query.message.delete()
