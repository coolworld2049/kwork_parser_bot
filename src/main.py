import asyncio

import polling
import webhook
from settings import settings


def main():
    if settings().BOT_RUN_MODE == "webhook":
        webhook.main()
    elif settings().BOT_RUN_MODE == "polling":
        asyncio.run(polling.main())
    else:
        raise ValueError(f"BOT_RUN_MODE={settings().BOT_RUN_MODE}")


if __name__ == "__main__":
    main()
