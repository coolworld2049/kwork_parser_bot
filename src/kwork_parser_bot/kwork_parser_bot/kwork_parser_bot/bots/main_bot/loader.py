from aiogram import Bot

from kwork_parser_bot.core.config import get_app_settings

main_bot = Bot(get_app_settings().BOT_TOKEN, parse_mode="HTML")
