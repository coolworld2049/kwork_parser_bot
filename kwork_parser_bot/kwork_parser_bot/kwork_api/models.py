from datetime import datetime

import pytz

from kwork_api.api.types import Project
from settings import get_settings


class KworkProject(Project):
    @classmethod
    def convert_to_datetime(cls, timestamp: float):
        return datetime.fromtimestamp(timestamp, tz=pytz.timezone(get_settings().TZ))

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
