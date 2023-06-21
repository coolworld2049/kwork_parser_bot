from aiogram.filters.callback_data import CallbackData


class CategoryCallback(CallbackData, prefix="cat"):
    name: str
    category_id: int
    subcategory_id: int | None


class MenuCallback(CallbackData, prefix="menu"):
    name: str
    action: str | None


class NavigationCallback(CallbackData, prefix="to"):
    to: str


class SchedulerCallback(CallbackData, prefix="sched"):
    name: str | None
    user_id: str | None
    action: str | None
    category_id: int | None
    subcategory_id: int | None
