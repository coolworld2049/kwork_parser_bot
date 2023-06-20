from aiogram.filters.callback_data import CallbackData


class CategoryCallback(CallbackData, prefix="category"):
    name: str = "category-selector"
    category_id: int
    selected_category_id: int | None
