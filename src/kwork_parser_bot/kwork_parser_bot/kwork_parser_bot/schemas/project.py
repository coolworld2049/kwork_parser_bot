from datetime import datetime

import pytz
from kwork.types import Project

from kwork_parser_bot.core.config import get_app_settings


class ProjectExtended(Project):
    @classmethod
    def convert_to_datetime(cls, timestamp: float):
        return datetime.fromtimestamp(
            timestamp, tz=pytz.timezone(get_app_settings().TIMEZONE)
        )

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

    @property
    def project_url(self):
        return f"https://kwork.ru/projects/{self.id}/view"
