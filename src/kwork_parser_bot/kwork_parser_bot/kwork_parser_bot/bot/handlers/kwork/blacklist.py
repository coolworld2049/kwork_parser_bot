from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from aredis_om import NotFoundError

from kwork_parser_bot.bot.callbacks import (
    MenuCallback,
    BlacklistCallback,
)
from kwork_parser_bot.bot.handlers.decorators import message_process
from kwork_parser_bot.bot.keyboards.kwork import (
    blacklist_menu_keyboard_builder,
)
from kwork_parser_bot.bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bot.loader import main_bot
from kwork_parser_bot.bot.states import BlacklistState
from kwork_parser_bot.services.kwork.schemas import Blacklist
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)


async def blacklist_menu(user: User, state: FSMContext):
    state_data = await state.get_data()
    with suppress(TelegramBadRequest, TypeError):
        for m_id in range(
            state_data.get("first_message_id"), state_data.get("current_message_id") + 1
        ):
            await main_bot.delete_message(user.id, m_id)
    builder = blacklist_menu_keyboard_builder()
    builder = menu_navigation_keyboard_builder(
        back_callback=MenuCallback(name="api").pack(),
        inline_buttons=builder.buttons,
    )
    try:
        blacklist = await Blacklist.find(Blacklist.telegram_user_id == user.id).first()
    except NotFoundError:
        blacklist = Blacklist(
            telegram_user_id=user.id,
        )
        await blacklist.save()
    message = await main_bot.send_message(
        user.id,
        render_template(
            "blacklist.html",
            blacklist=blacklist.usernames,
        ),
        reply_markup=builder.as_markup(),
    )
    await state.update_data(
        first_message_id=message.message_id, current_message_id=message.message_id
    )


@router.callback_query(
    MenuCallback.filter(F.name == "blacklist"),
)
async def blacklist_callback(
    query: CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    await query.message.delete()
    await blacklist_menu(query.from_user, state)


@router.callback_query(
    BlacklistCallback.filter(F.name == "blacklist"),
)
async def blacklist_add_rm(
    query: CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    await query.answer("Enter username")
    await state.update_data(callback_data=callback_data.dict())
    await state.set_state(BlacklistState.manage)


@router.message(BlacklistState.manage)
@message_process
async def blacklist_process(message: Message, state: FSMContext):
    state_data = await state.get_data()
    callback_data: MenuCallback = MenuCallback(**state_data.get("callback_data"))
    blacklist: Blacklist = await Blacklist.find(
        Blacklist.telegram_user_id == message.from_user.id
    ).first()
    usernames = blacklist.usernames.copy()
    try:
        if callback_data.action == "add":
            usernames.append(message.text)
        elif callback_data.action == "rm":
            usernames = blacklist.usernames.copy()
            usernames.remove(message.text)
    except Exception as e:
        raise ValueError(f"Input error")
    await blacklist.update(usernames=usernames)
    await blacklist_menu(message.from_user, state)
