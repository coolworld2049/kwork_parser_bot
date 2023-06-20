from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        render_template(
            "start.html",
            user=message.from_user,
            settings=get_app_settings(),
        )
    )
