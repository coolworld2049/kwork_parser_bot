import inspect

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from kwork.types import Category, Project
from loguru import logger

from kwork_parser_bot.bots.dispatcher import redis
from kwork_parser_bot.bots.main_bot.callbacks.base import CategoryCallback
from kwork_parser_bot.bots.main_bot.keyboards.action import action_keyboard_builder
from kwork_parser_bot.bots.main_bot.keyboards.category import category_keyboard_builder
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.states import CategoryState, SubcategoryState
from kwork_parser_bot.bots.main_bot.thirdparty.kwork.main import kwork_api, get_categories
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.schemas.action import Action
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.message(Command("categories"))
async def category(message: Message, state: FSMContext):
    categories = await get_categories(redis)
    builder = category_keyboard_builder(categories)
    builder.adjust(2)
    await message.answer(
        text="🤖 Categories Menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.set_data(data={"categories": categories})
    await state.set_state(CategoryState.select_subcategory)


@router.callback_query(
    CategoryCallback.filter(F.name == "category"), CategoryState.select_subcategory
)
async def subcategory(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    state_data = await state.get_data()
    categories: list[Category] = state_data.get("categories")
    builder = category_keyboard_builder(categories, callback_data.category_id, callback_name="subcategory")
    if not builder:
        logger.debug(
            f"category_keyboard_builder:{builder}, currentframe.f_code:{inspect.currentframe().f_code}"
        )
        return None
    builder.adjust(2)
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Subcategories Menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.update_data(data={"category_id": callback_data.category_id})
    await state.set_state(SubcategoryState.select_action)


@router.callback_query(
    CategoryCallback.filter(F.name == "subcategory"), SubcategoryState.select_action
)
async def subcategory_action(
    query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext
):
    state_data = await state.get_data()
    category_id: int = state_data.get("category_id")
    subcategory_id: int = callback_data.category_id

    actions = [
        Action(
            text="⚙️ Отслеживать новые заказы в категории",
            user_id=query.from_user.id,
            category_id=category_id,
            subcategory_id=subcategory_id,
            action="notify-new-orders"
        )
    ]
    builder = action_keyboard_builder(actions, category_id, subcategory_id)
    builder.adjust(1)
    await main_bot.send_message(
        query.from_user.id,
        text="🤖 Action Menu 🤖",
        reply_markup=builder.as_markup(),
    )


@router.message(Command("order_exchange"))
async def order_exchange(message: Message):
    projects: list[Project] = await kwork_api.get_projects(categories_ids=[11, 79])
    commands = {x.command: x.description for x in get_app_settings().BOT_COMMANDS}
    await message.answer(
        render_template(
            "order_exchange.html",
            bot_commands=commands,
        )
    )
