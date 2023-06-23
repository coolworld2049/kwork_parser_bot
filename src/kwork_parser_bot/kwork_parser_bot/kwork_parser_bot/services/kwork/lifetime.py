from aiogram import Bot
from kwork import Kwork

from kwork_parser_bot.core.config import get_app_settings


def init_kwork_api(bot: Bot):
    bot.kwork_api = Kwork(
        login=get_app_settings().KWORK_LOGIN,
        password=get_app_settings().KWORK_PASSWORD,
        phone_last=get_app_settings().KWORK_PHONE_LAST,
    )


async def shutdown_kwork_api(bot: Bot):
    await bot.kwork_api.close()
