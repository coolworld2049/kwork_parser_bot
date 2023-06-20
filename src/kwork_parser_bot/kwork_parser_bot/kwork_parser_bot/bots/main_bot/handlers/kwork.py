from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from kwork.types import Category, Project

from kwork_parser_bot.bots.main_bot.callbacks.order_exchange import CategoryCallback
from kwork_parser_bot.bots.main_bot.keyboards.category import category_keyboard_builder
from kwork_parser_bot.bots.main_bot.loader import kwork_api, main_bot
from kwork_parser_bot.bots.main_bot.states import CategoryState
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.message(Command("categories"))
async def categories(message: Message, state: FSMContext):
    categories: list[Category] = await kwork_api.get_categories()
    builder = category_keyboard_builder(categories)
    builder.adjust(2)
    await message.answer(
        text="🤖 Categories Menu 🤖",
        reply_markup=builder.as_markup(),
    )
    await state.set_data(data={"categories": categories})
    await state.set_state(CategoryState.select_subcategory)


@router.callback_query(CategoryCallback.filter(F.name == "category-selector"), CategoryState.select_subcategory)
async def subcategories(query: CallbackQuery, callback_data: CategoryCallback, state: FSMContext):
    state_data = await state.get_data()
    categories: list[Category] = state_data.get("categories")
    builder = category_keyboard_builder(categories, selected_category_id=callback_data.category_id)
    await main_bot.send_message(
        query.message.from_user.id,
        text="🤖 Subcategories Menu 🤖",
        reply_markup=builder.as_markup(),
    )


# @router.callback_query(CategoryCallback.filter(F.name == "category-selector"))
# async def subcategories(query: CallbackQuery, callback_data: CategoryCallback):
#     await query.answer(
#         text="🤖 Subcategories Menu 🤖",
#     )


# @router.message(CategoryState.category)
# async def subcategories(message: Message, state: FSMContext):
#     state_data = await state.get_data()
#     categories: list[Category] = state_data.get("categories")
#     builder = subcategory_keyboard_builder(categories)
#     await message.answer(
#         text="🤖 Subcategories Menu 🤖",
#         reply_markup=builder.as_markup(),
#     )
#     await state.set_state(CategoryState.subcategory)


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
