from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from kwork_parser_bot.db.models.botuser import BotUser
from kwork_parser_bot.db.models.kwork_account import KworkAccount

PydanticBotUser = sqlalchemy_to_pydantic(BotUser)
PydanticKworkAccount = sqlalchemy_to_pydantic(KworkAccount)
