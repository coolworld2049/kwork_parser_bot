from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from prisma.errors import RecordNotFoundError
from prisma.models import Blacklist
from prisma.types import BlacklistCreateInput

from loader import bot
from telegram_bot.callbacks import (
    MenuCallback,
    BlacklistCallback,
)
from telegram_bot.handlers.decorators import message_process_error
from telegram_bot.keyboards.kwork import (
    blacklist_menu_keyboard_builder,
)
from telegram_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from telegram_bot.states import BlacklistState
from template_engine import render_template

router = Router(name=__file__)


async def blacklist_menu(user: User, state: FSMContext):
    state_data = await state.get_data()
    with suppress(TelegramBadRequest, TypeError):
        for m_id in range(
            state_data.get("first_message_id"), state_data.get("current_message_id") + 1
        ):
            await bot.delete_message(user.id, m_id)
    builder = blacklist_menu_keyboard_builder()
    builder = menu_navigation_keyboard_builder(
        back_callback=MenuCallback(name="client").pack(),
        inline_buttons=builder.buttons,
    )
    blacklist = (
        await Blacklist.prisma().find_unique(where={"telegram_user_id": user.id}) or []
    )
    message = await bot.send_message(
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
@message_process_error
async def blacklist_process(message: Message, state: FSMContext):
    state_data = await state.get_data()
    callback_data: MenuCallback = MenuCallback(**state_data.get("callback_data"))
    try:
        blacklist = await Blacklist.prisma().find_unique_or_raise(
            where={"telegram_user_id": message.from_user.id}
        )
    except RecordNotFoundError as e:
        blacklist = await Blacklist.prisma().create(
            data=BlacklistCreateInput(
                telegram_user_id=message.from_user.id, usernames=[]
            )
        )
    new_blacklist = set(blacklist.usernames.copy())
    if callback_data.action == "add":
        new_blacklist.add(message.text)
    elif callback_data.action == "rm":
        new_blacklist.discard(message.text)
    await Blacklist.prisma().update(
        where={"telegram_user_id": message.from_user.id},
        data={"usernames": {"set": list(new_blacklist)}},
    )
    await blacklist_menu(message.from_user, state)
