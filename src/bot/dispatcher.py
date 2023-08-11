import pathlib

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import (
    RedisStorage,
    RedisEventIsolation,
)
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from bot.loader import redis
from bot.middlewares.services import ServicesMiddleware

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
