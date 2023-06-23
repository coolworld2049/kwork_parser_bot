from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger

from kwork_parser_bot.bots.dispatcher import redis
from kwork_parser_bot.bots.main_bot.callbacks import (
    KworkCategoryCallback,
    SchedulerCallback,
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.keyboards.kwork import (
    category_keyboard_builder,
    kwork_menu_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.scheduler import scheduler_jobs_keyboard_builder
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.states import SchedulerState
from kwork_parser_bot.bots.main_bot.thirdparty.kwork.main import (
    cached_categories,
    get_parent_category,
    get_category,
    kwork_api,
)
from kwork_parser_bot.schemas import SchedJob

sched_jobs_pkg = f"{'.'.join(str(__package__).split('.')[:-1])}.sched.jobs"

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "kwork"))
async def kwork_menu(query: CallbackQuery, state: FSMContext):
    sched_jobs = [  # Todo
        SchedJob(
            text="🔔 Receive account notifications",
            callback=SchedulerCallback(
                name="job",
                action="add",
                user_id=query.from_user.id,
            ),
            name="account notifications",
            func=f"{sched_jobs_pkg}:notify_about_kwork_notifications",
            args=(
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


@router.callback_query(MenuCallback.filter(F.name == "category"))
async def category(
    query: CallbackQuery, callback_data: KworkCategoryCallback, state: FSMContext
):
    await state.clear()
    categories = await cached_categories(redis, kwork_api=kwork_api)
    builder = category_keyboard_builder(categories, callback_name="subcategory")
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
    query: CallbackQuery, callback_data: KworkCategoryCallback, state: FSMContext
):
    categories = await cached_categories(redis, kwork_api=kwork_api)
    builder = category_keyboard_builder(
        categories, callback_data.category_id, callback_name="sched-job"
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


@router.callback_query(KworkCategoryCallback.filter(F.name == "sched-job"))
async def subcategory_sched_job(
    query: CallbackQuery, callback_data: KworkCategoryCallback, state: FSMContext
):
    state_data = await state.get_data()
    category_id: int = state_data.get("category_id")
    subcategory_id: int = callback_data.subcategory_id
    if not all([category_id, subcategory_id]):
        logger.debug(all([category_id, subcategory_id]))
        return None
    categories = await cached_categories(redis, kwork_api=kwork_api)
    parent_category = get_parent_category(categories, category_id)
    category = get_category(categories, parent_category.id, subcategory_id)

    notify_about_new_projects_callback = SchedulerCallback(
        name="job",
        action="add",
        category_id=category_id,
        subcategory_id=subcategory_id,
        user_id=query.from_user.id,
    )
    sched_jobs = [
        SchedJob(
            text="🆕 Notify about new projects",
            callback=notify_about_new_projects_callback,
            name=f"notifications by {parent_category.name}-{category.name}",
            func=f"{sched_jobs_pkg}:notify_about_new_projects",
            args=(
                query.from_user.id,
                query.from_user.id,
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
