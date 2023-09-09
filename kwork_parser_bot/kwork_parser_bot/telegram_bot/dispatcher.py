import pathlib

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import (
    RedisStorage,
    RedisEventIsolation,
)
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from loader import redis
from settings import get_settings
from telegram_bot.middlewares.acl import ACLMiddleware

dp = Dispatcher(
    events_isolation=RedisEventIsolation(redis),
    storage=RedisStorage(redis),
    name=pathlib.Path(__file__).name,
)
dp.callback_query.middleware(CallbackAnswerMiddleware())
if get_settings().is_bot_acl_enabled:
    dp.update.middleware(ACLMiddleware())
