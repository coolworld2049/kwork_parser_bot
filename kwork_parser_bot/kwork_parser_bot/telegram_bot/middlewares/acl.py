from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from loguru import logger

from settings import get_settings


class ACLMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")
        if (
            not get_settings().BOT_ACL_USER_IDS
            or not len(get_settings().BOT_ACL_USER_IDS) > 0
        ):
            logger.error(f"BOT_ACL_USER_IDS={get_settings().BOT_ACL_USER_IDS}")
            return None
        elif user.id not in get_settings().BOT_ACL_USER_IDS:
            logger.info(f"Access denied for user - {user.json()}")
            return None
        else:
            return await handler(event, data)
