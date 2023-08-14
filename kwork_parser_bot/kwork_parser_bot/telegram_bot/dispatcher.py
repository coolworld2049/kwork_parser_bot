import pathlib

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import (
    RedisStorage,
    RedisEventIsolation,
)
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from settings import get_settings
from loader import redis
from telegram_bot.middlewares.acl import ACLMiddleware

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
if get_settings().is_bot_acl_enabled:
    dp.update.middleware(ACLMiddleware())
