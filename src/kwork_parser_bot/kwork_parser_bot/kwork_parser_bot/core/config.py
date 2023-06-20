from functools import lru_cache

from kwork_parser_bot.core.settings.settings import Settings


@lru_cache
def get_app_settings() -> Settings:
    config = Settings
    return config()
