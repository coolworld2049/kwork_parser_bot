from aiogram import Router
from aiogram.filters import CommandStart, Command
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


@router.message(Command("help"))
async def help(message: Message):
    commands = {x.command: x.description for x in get_app_settings().BOT_COMMANDS}
    await message.answer(
        render_template(
            "help.html",
            bot_commands=commands,
        )
    )
