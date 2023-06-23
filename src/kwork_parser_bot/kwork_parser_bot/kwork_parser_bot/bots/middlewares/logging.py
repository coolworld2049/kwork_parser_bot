from pprint import pprint  # noqa
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from loguru import logger  # noqa


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        result = await handler(event, data)
        # pprint(event, compact=True)
        # pprint(data, compact=True)
        print(f"result:{result}\n")
        return result
