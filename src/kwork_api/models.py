from abc import ABC
from datetime import datetime

import pytz
from aredis_om import Field, JsonModel

from bot.loader import redis
from kwork_api.client.types import Project, Actor
from settings import settings


class BaseModel(JsonModel, ABC):
    class Meta:
        global_key_prefix = "kwork_api-client"
        database = redis


class Blacklist(BaseModel):
    telegram_user_id: int = Field(index=True, primary_key=True)
    usernames: list[str] | None = Field([], index=True)


class KworkActor(BaseModel, Actor):
    id: int = Field(index=True, primary_key=True)
    username: str = Field(index=True, full_text_search=True)

    class Meta:
        embedded = True


class KworkAccount(BaseModel):
    telegram_user_id: int = Field(index=True, primary_key=True)
    login: str | None = Field(index=True)
    password: str | None = Field(index=True)
    phone: str | None = Field(index=True)
    actor: KworkActor | None


class KworkProject(Project):
    @classmethod
    def convert_to_datetime(cls, timestamp: float):
        return datetime.fromtimestamp(timestamp, tz=pytz.timezone(settings().TIMEZONE))

    @property
    def time_left_datetime(self):
        return self.convert_to_datetime(float(self.time_left))

    @property
    def time_left_time(self):
        return self.time_left_datetime.time()

    @property
    def date_confirm_datetime(self):
        return self.convert_to_datetime(float(self.date_confirm))

    @property
    def date_confirm_time(self):
        return self.date_confirm_datetime.time()
