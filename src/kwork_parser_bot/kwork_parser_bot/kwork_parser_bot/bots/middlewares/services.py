from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from redis.asyncio.client import Redis


class ServicesMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        result = await handler(event, data)
        async with Redis(
            connection_pool=data.get("bot").redis_pool,
            single_connection_client=True,
        ) as redis:
            data["redis"] = redis
        data["kwork_api"] = data.get("bot").kwork_api
        data["sched"] = data.get("bot").sched
        return result
