from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kwork_parser_bot.db.models.kwork_account import KworkAccount
from kwork_parser_bot.db.session import get_db
from kwork_parser_bot.services.kwork.base_class import KworkCreds, KworkApi


class ServicesMiddleware(BaseMiddleware):
    @staticmethod
    async def provide_kwork_api(db: AsyncSession, user: User, cached_creds: KworkCreds):
        statement = await db.execute(
            select(KworkAccount).filter_by(telegram_id=user.id)
        )
        kwork_account_obj: KworkAccount = statement.scalar()
        kwork_account_data = kwork_account_obj.to_dict()
        if not KworkAccount.check_password(
            cached_creds.password, kwork_account_data.get("password")
        ):
            raise Exception("Bad kwork credentials")
        kwork_account_data.update({"password": cached_creds.password})
        return KworkApi(KworkCreds(**kwork_account_data))

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["kwork_api"] = None
        data["redis_pool"] = data.get("bot").__getattribute__("redis_pool")
        user: User = data.get("event_from_user")
        async with get_db() as db:
            try:
                cached_kwork_creds = await KworkCreds.get_cached(user.id)
                if not cached_kwork_creds:
                    raise ValueError(f"cached_kwork_creds: {cached_kwork_creds}")
                kwork_api = await self.provide_kwork_api(db, user, cached_kwork_creds)
                data["kwork_api"] = kwork_api
                logger.debug(kwork_api.__dict__)
            except Exception as e:
                logger.debug(e)
        result = await handler(event, data)
        if data.get("kwork_api"):
            await data.get("kwork_api").close()
        return result
