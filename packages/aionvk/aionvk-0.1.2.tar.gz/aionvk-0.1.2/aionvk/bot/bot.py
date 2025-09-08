import io
from typing import Any, Optional

from ..client import VKClient
from ..types import Callback


class Bot:
    """
    Высокоуровневый фасад для удобного взаимодействия с VK Bot API.
    Предоставляет методы для отправки и редактирования сообщений,
    а также для ответов на callback-события.
    """

    def __init__(self, token: str, **kwargs: Any):
        self.client = VKClient(token=token, **kwargs)

    async def send_message(
        self, peer_id: int, text: str, keyboard: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """
        Отправляет сообщение пользователю.

        :param peer_id: ID получателя.
        :param text: Текст сообщения.
        :param keyboard: JSON-строка с inline или reply клавиатурой.
        :param kwargs: Дополнительные параметры для метода messages.send.
        :return: Ответ от VK API.
        """
        return await self.client.send_message(
            peer_ids=peer_id, message=text, keyboard=keyboard, **kwargs
        )

    async def edit_message(
        self,
        peer_id: int,
        conversation_message_id: int,
        text: str,
        keyboard: Optional[str] = None,
        **kwargs: Any
    ):
        """
        Редактирует ранее отправленное сообщение.

        :param peer_id: ID диалога.
        :param conversation_message_id: ID сообщения в диалоге.
        :param text: Новый текст сообщения.
        :param keyboard: Новая JSON-строка с клавиатурой.
        :param kwargs: Дополнительные параметры для метода messages.edit.
        :return: Ответ от VK API.
        """
        return await self.client.edit_message(
            peer_id=peer_id,
            conversation_message_id=conversation_message_id,
            message=text,
            keyboard=keyboard,
            **kwargs
        )

    async def answer_callback(self, event: Callback) -> Any:
        """
        Подтверждает получение callback-события, убирая "часики" на кнопке.
        Не показывает никаких уведомлений пользователю.
        Это обязательный вызов для каждого callback-хендлера.
        """
        return await self.client.answer_event(
            event_id=event.event_id,
            user_id=event.user_id,
            peer_id=event.peer_id,
            event_data={},  # Пустой event_data для тихого ответа
        )

    async def show_snackbar(self, event: Callback, text: str) -> Any:
        """
        Показывает всплывающее уведомление (snackbar) пользователю.
        Также убирает "часики" на кнопке.
        """
        event_data = {"type": "show_snackbar", "text": text}
        return await self.client.answer_event(
            event_id=event.event_id,
            user_id=event.user_id,
            peer_id=event.peer_id,
            event_data=event_data,
        )

    async def upload_document(
        self, peer_id: int, file_io: io.BytesIO, filename: str
    ) -> Optional[str]:
        """
        Удобная обертка для загрузки документа.

        :param peer_id: ID диалога, куда будет отправлен документ.
        :param file_io: Файл в виде байтового потока (BytesIO).
        :param filename: Имя файла с расширением (например, 'report.txt').
        :return: Строка для вложения или None в случае ошибки.
        """
        return await self.client.upload_document(
            peer_id=peer_id, file_io=file_io, filename=filename
        )

    async def close(self):
        """Корректно закрывает HTTP-сессию клиента."""
        await self.client.close()

    def __call__(self, *args, **kwargs):
        """Позволяет использовать экземпляр Bot как асинхронный контекстный менеджер."""
        return self._session_context()

    async def _session_context(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
