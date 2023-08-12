import pathlib

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import (
    RedisStorage,
    RedisEventIsolation,
)
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from settings import settings
from telegram_bot.loader import redis
from telegram_bot.middlewares.acl import ACLMiddleware
from telegram_bot.middlewares.services import ServicesMiddleware

dp = Dispatcher(
    events_isolation=RedisEventIsolation(redis),
    storage=RedisStorage(
        redis,
        state_ttl=600,
        data_ttl=600,
    ),
    name=pathlib.Path(__file__).name,
)
dp.callback_query.middleware(CallbackAnswerMiddleware())
dp.update.middleware(ServicesMiddleware())
if settings().is_bot_acl_enabled:
    dp.update.middleware(ACLMiddleware())
