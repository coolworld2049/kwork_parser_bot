from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from redis.asyncio.client import Redis

from kwork_parser_bot.bots.middlewares.logging import LoggingMiddleware
from kwork_parser_bot.core.config import get_app_settings

redis = Redis(
    host=get_app_settings().REDIS_MASTER_HOST,
    port=get_app_settings().REDIS_MASTER_PORT_NUMBER,
    password=get_app_settings().REDIS_PASSWORD,
    db=get_app_settings().REDIS_DATABASE,
    max_connections=get_app_settings().REDIS_MAX_CONNECTIONS,
    encoding="utf-8",
)

dp = Dispatcher(
    storage=RedisStorage(redis, state_ttl=1800, data_ttl=1800)
    if get_app_settings().USE_REDIS
    else MemoryStorage()
)
dp.update.middleware(LoggingMiddleware()) if get_app_settings().STAGE == "dev" else None
dp.callback_query.middleware(CallbackAnswerMiddleware())
