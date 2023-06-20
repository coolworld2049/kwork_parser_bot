from aiogram.fsm.state import StatesGroup, State


class CategoryState(StatesGroup):
    select_subcategory = State()


class SubcategoryState(StatesGroup):
    select_action = State()
