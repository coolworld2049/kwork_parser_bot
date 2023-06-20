from aiogram.filters.callback_data import CallbackData


class CategoryCallback(CallbackData, prefix="cat"):
    name: str
    category_id: int
    subcategory_id: int | None


class SubcategoryActionCallback(CallbackData, prefix="subcat"):
    name: str
    action: str
    category_id: int
    subcategory_id: int | None
