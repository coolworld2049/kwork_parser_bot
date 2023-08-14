import asyncio

import polling
import webhook
from settings import get_settings


def main():
    if get_settings().BOT_RUN_MODE == "webhook":
        webhook.main()
    elif get_settings().BOT_RUN_MODE == "polling":
        asyncio.run(polling.main())
    else:
        raise ValueError(f"BOT_RUN_MODE={get_settings().BOT_RUN_MODE}")


if __name__ == "__main__":
    main()
