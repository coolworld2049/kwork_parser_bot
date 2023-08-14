from aiogram.filters.callback_data import CallbackData


class KworkCategoryCallback(CallbackData, prefix="category"):
    name: str
    category_id: int | None
    subcategory_id: int | None


class MenuCallback(CallbackData, prefix="menu"):
    name: str
    action: str | None
    message_id: int | None


class ConfirmCallback(CallbackData, prefix="confirm"):
    name: str
    answer: str


class SchedulerCallback(CallbackData, prefix="scheduler"):
    name: str | None
    action: str | None
    telegram_user_id: int | None
    category_id: int | None
    subcategory_id: int | None
    from_: str | None


class BlacklistCallback(CallbackData, prefix="blacklist"):
    name: str | None
    action: str | None
