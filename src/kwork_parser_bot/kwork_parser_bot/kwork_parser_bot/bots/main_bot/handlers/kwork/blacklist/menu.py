import json

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from redis.asyncio.client import Redis

from kwork_parser_bot.bots.main_bot.callbacks import (
    MenuCallback,
    BlacklistCallback,
)
from kwork_parser_bot.bots.main_bot.handlers.utils import message_process
from kwork_parser_bot.bots.main_bot.keyboards.kwork import (
    blacklist_menu_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.keyboards.navigation import (
    menu_navigation_keyboard_builder,
)
from kwork_parser_bot.bots.main_bot.loader import main_bot
from kwork_parser_bot.bots.main_bot.states import BlacklistState
from kwork_parser_bot.services.redis.lifetime import redis_pool
from kwork_parser_bot.template_engine import render_template

router = Router(name=__file__)
blacklist_redis_key_prefix = "blacklist"


async def blacklist_menu(user: User, state: FSMContext):
    state_data = await state.get_data()
    redis_key = f"{blacklist_redis_key_prefix}:{user.id}"
    builder = blacklist_menu_keyboard_builder()
    builder = menu_navigation_keyboard_builder(
        back_callback=MenuCallback(name="kwork").pack(),
        inline_buttons=builder.buttons,
    )
    async with Redis(connection_pool=redis_pool) as redis:
        # await redis.delete(redis_key)
        blacklist = await redis.get(redis_key)
        if not blacklist:
            blacklist = {"data": []}
            await redis.set(redis_key, json.dumps(blacklist))
            await redis.persist(redis_key)
        else:
            blacklist = json.loads(blacklist)
        await main_bot.send_message(
            user.id,
            render_template(
                "blacklist.html",
                blacklist=blacklist.get("data"),
            ),
            reply_markup=builder.as_markup(),
        )


@router.callback_query(
    MenuCallback.filter(F.name == "blacklist"),
)
async def blacklist(
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
    redis_key = f"{blacklist_redis_key_prefix}:{message.from_user.id}"
    async with Redis(connection_pool=redis_pool) as redis:
        blacklist = json.loads(await redis.get(redis_key))
        data = set(blacklist.get("data"))
        if callback_data.action == "add":
            data.add(message.text)
            await redis.set(redis_key, json.dumps({"data": list(data)}))
        elif callback_data.action == "rm":
            data.remove(message.text)
            await redis.set(redis_key, json.dumps({"data": list(data)}))

    await state.clear()
    await blacklist_menu(message.from_user, state)
