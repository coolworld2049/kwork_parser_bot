from aiogram import F, Router
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
from kwork_parser_bot.template_engine import render_template
from kwork_parser_bot.services.kwork.schemas import Blacklist

router = Router(name=__file__)
blacklist_redis_key_prefix = "blacklist"


async def blacklist_menu(user: User, state: FSMContext):
    state_data = await state.get_data()
    redis_key = f"{blacklist_redis_key_prefix}:{user.id}"
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
    await main_bot.send_message(
        user.id,
        render_template(
            "blacklist.html",
            blacklist=blacklist.usernames,
        ),
        reply_markup=builder.as_markup(),
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
    BlacklistCallback.filter(F.action == "add"),
)
async def blacklist_add(
    query: CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    builder = menu_navigation_keyboard_builder(
        back_callback=MenuCallback(name="blacklist").pack(),
    )
    await query.message.delete()
    message = await main_bot.send_message(
        query.from_user.id,
        "Add username",
        reply_markup=builder.as_markup(),
    )
    await state.update_data(callback_data=callback_data.dict())
    await state.set_state(BlacklistState.manage)


@router.callback_query(
    BlacklistCallback.filter(F.name == "blacklist" and F.action == "rm"),
)
async def blacklist_delete(
    query: CallbackQuery, callback_data: MenuCallback, state: FSMContext
):
    builder = menu_navigation_keyboard_builder(
        back_callback=MenuCallback(name="blacklist").pack(),
    )
    await query.message.delete()
    message = await main_bot.send_message(
        query.from_user.id,
        "Delete username",
        reply_markup=builder.as_markup(),
    )
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
    await state.clear()
    await blacklist_menu(message.from_user, state)
