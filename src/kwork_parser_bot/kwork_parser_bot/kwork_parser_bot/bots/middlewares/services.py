from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.db.session import get_db
from kwork_parser_bot.services.kwork.base_class import KworkCreds
from kwork_parser_bot.services.kwork.lifetime import get_user_kwork_api


class ServicesMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        event_from_user: User = data.get("event_from_user")

        data["redis_pool"] = data.get("bot").__getattribute__("redis_pool")

        async with get_db() as db:
            data["db"] = db

        if event_from_user.id == get_app_settings().BOT_OWNER_ID:
            kwork_creds = KworkCreds(
                login=get_app_settings().KWORK_LOGIN,
                password=get_app_settings().KWORK_PASSWORD,
                phone_last=get_app_settings().KWORK_PHONE_LAST,
            )
        else:
            kwork_creds = None
        async with get_user_kwork_api(kwork_creds) as kwork_api:
            if data.get("kwork_api"):
                data.get("bot").__delattr__("kwork_api")
            data["kwork_api"] = kwork_api
        data["scheduler"] = data.get("bot").__getattribute__("scheduler")
        result = await handler(event, data)
        return result
