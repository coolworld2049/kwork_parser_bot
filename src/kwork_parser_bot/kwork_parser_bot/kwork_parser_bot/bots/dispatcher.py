from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from kwork_parser_bot.bots.middlewares.logging import LoggingMiddleware

dp = Dispatcher()
dp.update.middleware(LoggingMiddleware())
dp.callback_query.middleware(CallbackAnswerMiddleware())
