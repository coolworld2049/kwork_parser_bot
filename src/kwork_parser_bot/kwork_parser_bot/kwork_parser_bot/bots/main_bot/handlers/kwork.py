import inspect

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from apscheduler.triggers.cron import CronTrigger
from cron_validator import CronValidator
from kwork.types import Category
from loguru import logger

from kwork_parser_bot.bots.dispatcher import redis
from kwork_parser_bot.bots.main_bot.callbacks.all import (
    CategoryCallback,
    SchedulerCallback,
    MenuCallback,
)
from kwork_parser_bot.bots.main_bot.keyboards.action import action_keyboard_builder
from kwork_parser_bot.bots.main_bot.keyboards.category import category_keyboard_builder
from kwork_parser_bot.bots.main_bot.keyboards.navigation import (
    navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot, async_scheduler
from kwork_parser_bot.bots.main_bot.scheduler_jobs.notify_about_new_projects import (
    notify_about_new_projects,
)
from kwork_parser_bot.bots.main_bot.states import CategoryState, SchedulerState
from kwork_parser_bot.bots.main_bot.thirdparty.kwork.main import cached_categories
from kwork_parser_bot.schemas import Action
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.callback_query(MenuCallback.filter(F.name == "kwork"))
async def category(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    categories = await cached_categories(redis)
    builder = category_keyboard_builder(categories)
    builder.adjust(2)
    builder = navigation_keyboard_builder(
        builder,
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Categories Menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.clear()
    await state.set_data(data={"categories": categories})
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
    builder = navigation_keyboard_builder(
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
    category_id: int = state_data.get("category_id")
    subcategory_id: int = callback_data.category_id
    subcategory_actions = [
        Action(
            text="⚙️ Уведомлять о новых проектах в подкатегории",
            callback=SchedulerCallback(
                name="job",
                user_id=query.from_user.id,
                category_id=category_id,
                subcategory_id=subcategory_id,
            ),
        )
    ]
    builder = action_keyboard_builder(subcategory_actions)
    builder.adjust(1)
    builder = navigation_keyboard_builder(
        builder,
        back_callback=MenuCallback(name="kwork").pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Action Menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.update_data(
        {"actions": subcategory_actions, "subcategory_id": subcategory_id}
    )
    await state.set_state(SchedulerState.add_job_process_input)
    await query.message.delete()


@router.callback_query(
    SchedulerCallback.filter(F.name == "job"), SchedulerState.add_job_process_input
)
async def scheduler_add_job_process_trigger(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    await state.set_state(SchedulerState.add_job)
    builder = navigation_keyboard_builder(
        back_callback=MenuCallback(name="kwork").pack(),
        menu_callback=MenuCallback(name="start").pack(),
    )
    message = await main_bot.send_message(
        query.from_user.id,
        render_template(
            "job_cron_trigger.html",
        ),
        reply_markup=builder.as_markup()
    )
    await query.message.delete()
    await state.update_data(prev_message_id=message.message_id)


@router.message(SchedulerState.add_job)
async def scheduler_add_job_process(message: Message, state: FSMContext):
    if not CronValidator.parse(message.text):
        await message.answer("Wrong cron expression")
        return None
    state_data = await state.get_data()
    await main_bot.delete_message(message.from_user.id, state_data.get("prev_message_id"))
    await state.update_data(data={"cron_trigger": message.text})
    actions: list[Action] = state_data.get("actions")
    categories: list[Category] = state_data.get("categories")
    category_id: int = state_data.get("category_id")
    subcategory_id: int = state_data.get("subcategory_id")
    job_id = actions[0].callback.pack()

    job = async_scheduler.add_job(
        notify_about_new_projects,
        CronTrigger.from_crontab(message.text),
        kwargs={
            "user_id": message.from_user.id,
            "callback": actions[0].callback.pack(),
            "categories_ids": [category_id],
        },
        id=job_id,
        name=actions[0].callback.pack(),
    )
    builder = navigation_keyboard_builder(
        menu_callback=MenuCallback(name="start").pack(),
    )
    await main_bot.send_message(
        message.from_user.id,
        render_template("scheduler_jobs.html", jobs=[job.__getstate__()]),
        reply_markup=builder.as_markup()
    )
    await state.clear()
