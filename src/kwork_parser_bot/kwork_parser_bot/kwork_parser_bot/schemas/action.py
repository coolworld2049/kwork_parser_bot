from pydantic import BaseModel

from kwork_parser_bot.bots.main_bot.callbacks import SchedulerCallback


class Action(BaseModel):
    text: str
    name: str
    callback: SchedulerCallback
