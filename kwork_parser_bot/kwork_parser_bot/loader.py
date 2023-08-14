from aiogram import Bot
from prisma import Prisma
from redis.asyncio import Redis, ConnectionPool

from scheduler.scheduler import Scheduler
from settings import get_settings

redis = Redis.from_url(get_settings().redis_url)
redis_pool = ConnectionPool.from_url(get_settings().redis_url)
scheduler = Scheduler(timezone=get_settings().TZ)
bot = Bot(get_settings().BOT_TOKEN, parse_mode="HTML")
prisma = Prisma(auto_register=True)
