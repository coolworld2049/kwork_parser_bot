from sqlalchemy import text

from kwork_parser_bot.core.config import get_app_settings
from kwork_parser_bot.db.base import Base
from kwork_parser_bot.db.models import load_all_models
from kwork_parser_bot.db.models.bot_user import BotUser
from kwork_parser_bot.db.models.kwork_account import KworkAccount
from kwork_parser_bot.db.session import engine, get_db


async def create_database():
    load_all_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if get_app_settings().TEST_DATA:
        async with get_db() as db:
            db.add(
                BotUser(
                    id=get_app_settings().BOT_OWNER_ID,
                    is_bot=False,
                    first_name="",
                )
            )
        async with get_db() as db:
            db.add(
                KworkAccount(
                    telegram_id=get_app_settings().BOT_OWNER_ID,
                    login=get_app_settings().TEST_KWORK_LOGIN,
                    password=KworkAccount.get_hashed_password(
                        get_app_settings().TEST_KWORK_PASSWORD
                    ),
                    phone=get_app_settings().TEST_KWORK_PHONE,
                )
            )


async def drop_database() -> None:
    load_all_models()
    async with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{get_app_settings().POSTGRESQL_DATABASE}' "
            "AND pid <> pg_backend_pid();"
        )
        await conn.execute(text(disc_users))
        await conn.execute(
            text(f'DROP DATABASE "{get_app_settings().POSTGRESQL_DATABASE}"')
        )
