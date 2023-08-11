from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aredis_om import NotFoundError
from loguru import logger

from kwork_api.kwork import KworkApi
from kwork_api.models import KworkAccount


class ServicesMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["kwork_api"] = None
        try:
            user = data.get("event_from_user")
            kwork_account: KworkAccount = await KworkAccount.find(
                KworkAccount.telegram_user_id == user.id
            ).first()
            data["kwork_api"] = KworkApi(kwork_account)
            logger.debug(f"kwork account - {data['kwork_api'].__dict__}")
        except NotFoundError as ne:
            logger.error(ne.__class__.__name__)
        except Exception as e:
            logger.error(e)
        result = await handler(event, data)
        if data.get("kwork_api"):
            await data.get("kwork_api").close()
        return result
