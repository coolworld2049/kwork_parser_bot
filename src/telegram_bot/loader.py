import os

from aiogram import Bot
from redis.asyncio import ConnectionPool
from redis.asyncio import Redis

from scheduler.scheduler import Scheduler
from settings import settings

os.environ["REDIS_OM_URL"] = settings().redis_url
redis = Redis.from_url(settings().redis_url)
redis_pool = ConnectionPool.from_url(settings().redis_url)
scheduler = Scheduler(timezone=settings().TIMEZONE)
bot = Bot(settings().BOT_TOKEN, parse_mode="HTML")
