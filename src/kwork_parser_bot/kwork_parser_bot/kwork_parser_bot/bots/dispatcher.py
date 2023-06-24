import pathlib

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, RedisEventIsolation
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from redis.asyncio import Redis

from kwork_parser_bot.bots.middlewares.services import ServicesMiddleware
from kwork_parser_bot.core.config import get_app_settings

redis = Redis(
    host=get_app_settings().REDIS_MASTER_HOST,
    port=get_app_settings().REDIS_MASTER_PORT_NUMBER,
    password=get_app_settings().REDIS_PASSWORD,
    db=get_app_settings().REDIS_DATABASE,
    max_connections=get_app_settings().REDIS_MAX_CONNECTIONS,
)
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
