from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from loguru import logger

from settings import settings


class ACLMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")
        if not settings().BOT_ACL_USER_IDS or not len(settings().BOT_ACL_USER_IDS) > 0:
            logger.error(f"BOT_ACL_USER_IDS={settings().BOT_ACL_USER_IDS}")
            return None
        if user.id not in settings().BOT_ACL_USER_IDS:
            logger.info(f"Access denied for user - {user.json()}")
            return None
