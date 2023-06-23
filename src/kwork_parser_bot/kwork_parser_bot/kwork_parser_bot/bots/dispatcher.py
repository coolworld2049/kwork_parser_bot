import pathlib

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, RedisEventIsolation
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from kwork_parser_bot.bots.middlewares.services import ServicesMiddleware
from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.services.redis.main import redis

dp = Dispatcher(
    events_isolation=RedisEventIsolation(redis)
    if get_app_settings().REDIS_MASTER_HOST
    else None,
    storage=RedisStorage(redis, state_ttl=600, data_ttl=600)
    if get_app_settings().REDIS_MASTER_HOST
    else MemoryStorage(),
    name=pathlib.Path(__file__).name,
)
dp.callback_query.middleware(CallbackAnswerMiddleware())
dp.update.middleware(ServicesMiddleware())
