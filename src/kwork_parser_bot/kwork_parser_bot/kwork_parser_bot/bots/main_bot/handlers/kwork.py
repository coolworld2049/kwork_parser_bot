import inspect

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.triggers.cron import CronTrigger
from cron_validator import CronValidator
from kwork.types import Category
from loguru import logger

from kwork_parser_bot.bots.dispatcher import redis
from kwork_parser_bot.bots.main_bot.callbacks import (
    CategoryCallback,
    SchedulerCallback,
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.handlers.start import start_message
from kwork_parser_bot.bots.main_bot.keyboards.kwork import (
    category_keyboard_builder,
    category_action_keyboard_builder,
    kwork_menu_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.menu import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot, async_scheduler
from kwork_parser_bot.bots.main_bot.sched.jobs.notify_about_new_projects import (
    notify_about_new_projects,
)
from kwork_parser_bot.bots.main_bot.states import CategoryState, SchedulerState
from kwork_parser_bot.bots.main_bot.thirdparty.kwork.main import (
    cached_categories,
    get_parent_category,
    get_category,
)
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.schemas import Action
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "kwork"))
async def kwork_menu(query: CallbackQuery):
    builder = kwork_menu_keyboard_builder()
    builder = menu_navigation_keyboard_builder(
        builder, menu_callback=MenuCallback(name="start").pack()
    )
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Kwork Menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await query.message.delete()


@router.callback_query(MenuCallback.filter(F.name == "category" and F.action == "get"))
async def category(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    categories = await cached_categories(redis)
    builder = category_keyboard_builder(categories)
    builder.adjust(2)
    builder = menu_navigation_keyboard_builder(
        builder,
        back_callback=MenuCallback(name="kwork").pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Categories Menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.clear()
    await state.update_data(data={"categories": categories})
    await state.set_state(CategoryState.select_subcategory)
    await query.message.delete()


@router.callback_query(
    CategoryCallback.filter(F.name == "category"), CategoryState.select_subcategory
)
async def subcategory(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    state_data = await state.get_data()
    categories: list[Category] = state_data.get("categories")
    builder = category_keyboard_builder(
        categories, callback_data.category_id, callback_name="subcategory"
    )
    if not builder:
        logger.debug(f"{inspect.currentframe().f_code}: {builder}")
        return None
    builder.adjust(2)
    builder = menu_navigation_keyboard_builder(
        builder,
        back_callback=MenuCallback(name="kwork").pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Subcategories Menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.update_data(data={"category_id": callback_data.category_id})
    await state.set_state(SchedulerState.select_action)
    await query.message.delete()


@router.callback_query(
    CategoryCallback.filter(F.name == "subcategory"), SchedulerState.select_action
)
async def subcategory_action(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    state_data = await state.get_data()
    categories: list[Category] = state_data.get("categories")
    category_id: int = state_data.get("category_id")
    subcategory_id: int = callback_data.category_id
    parent_category = get_parent_category(categories, category_id)
    category = get_category(categories, parent_category.id, subcategory_id)
    action_name = f"{parent_category.name},{category.name}"
    actions = [
        Action(
            text="⚙️ Уведомлять о новых проектах в подкатегории",
            name=action_name,
            callback=SchedulerCallback(
                name="job",
                action="add",
                category_id=category_id,
                subcategory_id=subcategory_id,
                user_id=query.from_user.id,
            ),
        )
    ]
    builder = category_action_keyboard_builder(actions)
    builder.adjust(1)
    builder = menu_navigation_keyboard_builder(
        builder,
        back_callback=MenuCallback(name="kwork").pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Action Menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.update_data({"actions": actions, "subcategory_id": subcategory_id})
    await state.set_state(SchedulerState.add_job_process_input)
    await query.message.delete()


@router.callback_query(
    SchedulerCallback.filter(F.name == "job" and F.action == "add"),
    SchedulerState.add_job_process_input,
)
async def scheduler_add_job_trigger_process(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    await state.set_state(SchedulerState.add_job)
    builder = menu_navigation_keyboard_builder(
        back_callback=MenuCallback(name="kwork").pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    message = await main_bot.send_message(
        query.from_user.id,
        render_template(
            "cron.html",
        ),
        reply_markup=builder.as_markup(),
    )
    await query.message.delete()
    await state.update_data(prev_message_id=message.message_id)


@router.message(SchedulerState.add_job)
async def scheduler_add_job_process(message: Message, state: FSMContext):
    if not CronValidator.parse(message.text):
        await message.answer("Wrong cron expression")
        return None
    state_data = await state.get_data()
    await main_bot.delete_message(
        message.from_user.id, state_data.get("prev_message_id")
    )
    await state.update_data(data={"cron_trigger": message.text})
    actions: list[Action] = state_data.get("actions")
    category_id: int = state_data.get("category_id")
    subcategory_id: int = state_data.get("subcategory_id")

    job_id = actions[0].callback.pack()
    try:
        cron_trigger = CronTrigger(jitter=120).from_crontab(
            message.text, timezone=get_app_settings().TIMEZONE
        )
        job = async_scheduler.add_job(
            notify_about_new_projects,
            cron_trigger,
            args=(
                message.from_user.id,
                [category_id],
            ),
            id=job_id,
            name=actions[0].name,
        )
    except ConflictingIdError:
        await message.answer("Job with this id already exist")
        return None
    await state.clear()
    await start_message(message, state)
