import collections
import logging
import typing
import urllib.parse

import aiohttp

from .exceptions import KworkException
from .types import (
    User,
    Actor,
    Dialog,
    MessageModel,
    Category,
    Project,
    Connects,
)

logger = logging.getLogger(__name__)
Handler = collections.namedtuple(
    "Handler", ["func", "text", "on_start", "text_contains"]
)


class Kwork:
    def __init__(
        self,
        login: str,
        password: str,
        proxy: typing.Optional[str] = None,
        phone: typing.Optional[str] = None,
    ):
        connector: typing.Optional[aiohttp.BaseConnector] = None

        if proxy is not None:
            try:
                from aiohttp_socks import ProxyConnector
            except ImportError:
                raise ImportError(
                    "You have to install aiohttp_socks for using"
                    " proxy, make it by pip install aiohttp_socks"
                )
            connector = ProxyConnector.from_url(proxy)

        self.session = aiohttp.ClientSession(connector=connector)
        self.host = "https://api.kwork.ru/{}"
        self.login = login
        self.password = password
        self._token: typing.Optional[str] = None
        self.phone_last = phone[-4:] if phone else None

    @property
    async def token(self) -> str:
        if self._token is None:
            self._token = await self.get_token()
        return self._token

    @token.setter
    async def token(self, value):
        self._token = value

    async def api_request(
        self, method: str, api_method: str, **params
    ) -> typing.Union[dict, typing.NoReturn]:
        params = {k: v for k, v in params.items() if v is not None}
        logging.debug(
            f"making {method} request on /{api_method} with params - {params}"
        )
        async with self.session.request(
            method=method,
            url=self.host.format(api_method),
            headers={"Authorization": "Basic bW9iaWxlX2FwaTpxRnZmUmw3dw=="},
            params=params,
        ) as resp:
            if resp.content_type != "application/json":
                error_text: str = await resp.text()
                raise KworkException(error_text)
            json_response: dict = await resp.json()
            if not json_response["success"]:
                raise KworkException(json_response["error"])
            logging.debug(f"result of request on /{api_method} - {json_response}")
            return json_response

    async def close(self) -> None:
        await self.session.close()

    async def get_token(self) -> str:
        resp: dict = await self.api_request(
            method="post",
            api_method="signIn",
            login=self.login,
            password=self.password,
            phone_last=self.phone_last,
        )
        return resp["response"]["token"]

    async def get_me(self) -> Actor:
        actor = await self.api_request(
            method="post", api_method="actor", token=await self.token
        )
        return Actor(**actor["response"])

    async def get_user(self, telegram_user_id: int) -> User:
        """
        :param telegram_user_id: you can find it in dialogs
        :return:
        """
        user = await self.api_request(
            method="post",
            api_method="user",
            id=telegram_user_id,
            token=await self.token,
        )
        print(user)
        return User(**user["response"])

    async def set_typing(self, recipient_id: int) -> dict:
        resp = await self.api_request(
            method="post",
            api_method="typing",
            recipientId=recipient_id,
            token=await self.token,
        )
        return resp

    async def get_all_dialogs(self) -> typing.List[Dialog]:
        page = 1
        dialogs: typing.List[Dialog] = []

        while True:
            dialogs_page = await self.api_request(
                method="post",
                api_method="dialogs",
                filter="all",
                page=page,
                token=await self.token,
            )
            if not dialogs_page["response"]:
                break

            for dialog in dialogs_page["response"]:
                dialogs.append(Dialog(**dialog))
            page += 1

        return dialogs

    async def set_offline(self) -> dict:
        return await self.api_request(
            method="post", api_method="offline", token=await self.token
        )

    async def get_dialog_with_user(self, user_name: str) -> typing.List[MessageModel]:
        page = 1
        dialog: typing.List[MessageModel] = []

        while True:
            messages_dict: dict = await self.api_request(
                method="post",
                api_method="inboxes",
                username=user_name,
                page=page,
                token=await self.token,
            )
            if not messages_dict.get("response"):
                break
            for message in messages_dict["response"]:
                dialog.append(MessageModel(**message))

            if page == messages_dict["paging"]["pages"]:
                break
            page += 1

        return dialog

    async def get_worker_orders(self) -> dict:
        return await self.api_request(
            method="post",
            api_method="workerOrders",
            filter="all",
            token=await self.token,
        )

    async def get_payer_orders(self) -> dict:
        return await self.api_request(
            method="post",
            api_method="payerOrders",
            filter="all",
            token=await self.token,
        )

    async def get_notifications(self) -> dict:
        return await self.api_request(
            method="post",
            api_method="notifications",
            token=await self.token,
        )

    async def get_categories(self) -> typing.List[Category]:
        raw_categories = await self.api_request(
            method="post",
            api_method="categories",
            type="1",
            token=await self.token,
        )
        categories = []
        for dict_category in raw_categories["response"]:
            category = Category(**dict_category)
            categories.append(category)
        return categories

    async def get_connects(self) -> Connects:
        raw_projects = await self.api_request(
            method="post",
            api_method="projects",
            categories="",
            token=await self.token,
        )
        return Connects(**raw_projects["connects"])

    async def get_projects(
        self, categories_ids: typing.List[int]
    ) -> typing.List[Project]:
        # TODO: pages

        raw_projects = await self.api_request(
            method="post",
            api_method="projects",
            categories=",".join(str(category) for category in categories_ids),
            token=await self.token,
        )
        projects = []
        for dict_project in raw_projects["response"]:
            project = Project(**dict_project)
            projects.append(project)
        return projects

    async def _get_channel(self) -> str:
        channel = await self.api_request(
            method="post", api_method="getChannel", token=await self.token
        )
        return channel["response"]["channel"]

    async def send_message(self, telegram_user_id: int, text: str) -> dict:  # noqa
        logging.debug(f"Sending message for {telegram_user_id} with text - {text}")
        resp = await self.session.post(
            f"{self.host.format('inboxCreate')}"
            f"?telegram_user_id={telegram_user_id}"
            f"&text={urllib.parse.quote(text)}&token={await self.token}",
            headers={"Authorization": "Basic bW9iaWxlX2FwaTpxRnZmUmw3dw=="},
        )
        json_resp = await resp.json()
        logging.debug(f"result of sending - {json_resp}")
        return json_resp

    async def delete_message(self, message_id) -> dict:
        return await self.api_request(
            method="post",
            api_method="inboxDelete",
            id=message_id,
            token=await self.token,
        )
