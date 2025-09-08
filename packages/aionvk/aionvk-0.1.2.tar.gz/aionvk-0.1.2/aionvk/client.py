import io
import json
from random import randint
from typing import Any, List, Optional, Dict, Union

from loguru import logger
import httpx
from pydantic import BaseModel, ValidationError

from .exceptions import APIError
from .types import VKUser


class VKAPIErrorDetail(BaseModel):
    error_code: int
    error_msg: str


class VKAPIErrorResponse(BaseModel):
    error: VKAPIErrorDetail


class VKClient:
    """Низкоуровневый клиент для VK API."""

    def __init__(self, token: str, api_version: str = "5.199"):
        if not token:
            raise ValueError("VKClient требует токен для инициализации")
        self.token = token
        self.api_version = api_version
        self.api_url = "https://api.vk.ru/method/"
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Ленивая инициализация httpx.AsyncClient."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient()
        return self._http_client

    async def close(self):
        """Закрывает httpx.AsyncClient."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def _make_request(self, method: str, params: Optional[dict] = None) -> Any:
        """
        Выполняет POST-запрос к VK API.
        Автоматически обрабатывает ошибки.
        """
        request_params = params or {}
        request_params["access_token"] = self.token
        request_params["v"] = self.api_version

        client = await self._get_client()

        try:
            response = await client.post(f"{self.api_url}{method}", data=request_params)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                try:
                    err = VKAPIErrorResponse.model_validate(data).error
                    logger.error(
                        f"VK API Error calling method '{method}'. "
                        f"Code: {err.error_code}, Message: '{err.error_msg}'"
                    )
                    raise APIError(err.error_code, err.error_msg)
                except ValidationError:
                    logger.error(
                        f"Unknown VK API Error structure. Method: '{method}', Response: {data}"
                    )
                    raise APIError(
                        -1, f"Неизвестная структура ошибки от VK: {data.get('error')}"
                    )

            return data.get("response")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error while requesting '{method}': {e}")
            raise e

    async def get_users(
        self, user_ids: Union[str, List[str]], fields: str = None
    ) -> Optional[List[VKUser]]:
        """
        Получение информации о пользователях.

        Args:
            user_ids: ID или список ID.
            fields: Доп. поля.

        Docs:
            https://dev.vk.com/method/users.get
        """
        if isinstance(user_ids, list):
            user_ids = ",".join(map(str, user_ids))

        params = {"user_ids": user_ids}
        if fields:
            params["fields"] = fields
        response = await self._make_request(method="users.get", params=params)
        return [VKUser.model_validate(item) for item in response] if response else None

    async def send_message(
        self, peer_ids: int | List[int], message: str, **kwargs: Any
    ) -> Any:
        """
        Отправка сообщения.

        Args:
            peer_ids: ID получателя или список.
            message: Текст сообщения.

        Docs:
            https://dev.vk.com/method/messages.send
        """
        if isinstance(peer_ids, int):
            peer_ids = [peer_ids]

        params = {
            "peer_ids": ",".join(map(str, peer_ids)),
            "message": message,
            "random_id": randint(0, 2**32),
        }
        params.update(kwargs)
        return await self._make_request(method="messages.send", params=params)

    async def edit_message(self, peer_id: int, message: str, **kwargs: Any) -> Any:
        """
        Редактирование сообщения.

        Args:
            peer_id: ID чата или пользователя.
            message: Новый текст.

        Docs:
            https://dev.vk.com/method/messages.edit
        """
        params = {"peer_id": peer_id, "message": message}
        params.update(kwargs)
        return await self._make_request(method="messages.edit", params=params)

    async def answer_event(
        self,
        event_id: str,
        user_id: int,
        peer_id: int,
        event_data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Ответ на callback-событие.

        Args:
            event_id: ID события.
            user_id: ID пользователя.
            peer_id: ID чата.
            event_data: JSON-данные.

        Docs:
            https://dev.vk.com/method/messages.sendMessageEventAnswer
        """
        params = {
            "event_id": event_id,
            "user_id": user_id,
            "peer_id": peer_id,
        }
        if event_data:
            params["event_data"] = json.dumps(event_data)
        return await self._make_request(
            method="messages.sendMessageEventAnswer", params=params
        )

    async def upload_document(
        self, peer_id: int, file_io: io.BytesIO, filename: str
    ) -> Optional[str]:
        """
        Загрузка документа и получение attachment-строки.

        Args:
            peer_id: ID назначения.
            file_io: Файл (BytesIO).
            filename: Имя файла.

        Docs:
            https://dev.vk.com/method/docs.getMessagesUploadServer
        """
        try:
            upload_server_info = await self._make_request(
                "docs.getMessagesUploadServer", {"type": "doc", "peer_id": str(peer_id)}
            )
            if not upload_server_info or "upload_url" not in upload_server_info:
                logger.error("Не удалось получить URL для загрузки документа.")
                return None
            upload_url = upload_server_info["upload_url"]

            client = await self._get_client()
            files = {"file": (filename, file_io)}
            upload_response = await client.post(upload_url, files=files)
            upload_response.raise_for_status()
            upload_data = upload_response.json()

            if "file" not in upload_data:
                logger.error(
                    f"Ответ от сервера загрузки не содержит поля 'file': {upload_data}"
                )
                return None

            save_response = await self._make_request(
                "docs.save", {"file": upload_data["file"], "title": filename}
            )
            if not save_response or "doc" not in save_response:
                logger.error(
                    f"Не удалось сохранить документ на сервере VK: {save_response}"
                )
                return None

            doc_data = save_response["doc"]
            owner_id = doc_data["owner_id"]
            doc_id = doc_data["id"]

            return f"doc{owner_id}_{doc_id}"

        except Exception as e:
            logger.exception(f"Критическая ошибка при загрузке документа: {e}")
            return None

    async def get_donut_subscribers(self, group_id: int) -> Optional[List[int]]:
        """
        Получение ID подписчиков VK Donut.

        Args:
            group_id: ID группы.

        Docs:
            https://dev.vk.com/method/groups.getMembers
        """
        all_donuts = []
        offset = 0
        count = 1000

        try:
            while True:
                response = await self._make_request(
                    "groups.getMembers",
                    {
                        "group_id": group_id,
                        "filter": "donut",
                        "offset": offset,
                        "count": count,
                    },
                )
                if response and "items" in response:
                    all_donuts.extend(response["items"])
                    if len(response["items"]) < count:
                        break
                    offset += count
                else:
                    break
            return all_donuts
        except Exception as e:
            logger.exception(f"Ошибка при получении подписчиков VK Donut: {e}")
            return None
