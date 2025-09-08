import json
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, model_validator


class BaseEvent(BaseModel):
    """
    Базовая модель для всех событий, получаемых от VK.
    Обеспечивает наличие ключевых полей для роутинга и ответов.
    """

    user_id: int
    peer_id: int
    payload: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"
        populate_by_name = True


class Message(BaseEvent):
    """
    Модель для события 'message_new'.
    Представляет собой входящее сообщение от пользователя.
    """

    user_id: int = Field(..., alias="from_id")
    text: str
    conversation_message_id: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def extract_message_from_event(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлекает объект 'message' из общей структуры события 'message_new'.
        Это позволяет инициализировать модель напрямую из event['object'].
        """
        if "message" in data and isinstance(data["message"], dict):
            # Переносим 'client_info' на верхний уровень для удобства
            # если он понадобится в будущем.
            if "client_info" in data:
                data["message"]["client_info"] = data["client_info"]
            return data["message"]
        return data

    @model_validator(mode="before")
    @classmethod
    def parse_payload_from_str(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Преобразует строковый payload в dict.
        """
        payload_str = data.get("payload")
        if payload_str and isinstance(payload_str, str):
            data["payload"] = json.loads(payload_str)
        return data


class Callback(BaseEvent):
    """
    Модель для события 'message_event'.
    Представляет собой нажатие на inline (callback) кнопку.
    """

    event_id: str
    conversation_message_id: int

    @model_validator(mode="before")
    @classmethod
    def parse_payload_from_str(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Преобразует строковый payload в dict, если он пришел в виде строки.
        """
        payload_str = data.get("payload")
        if payload_str and isinstance(payload_str, str):
            data["payload"] = json.loads(payload_str)
        return data


class VKUser(BaseModel):
    """Модель для данных пользователя, получаемых через users.get."""

    id: int
    first_name: str
    last_name: str
    bdate: Optional[str] = None
    sex: Optional[int] = None


VKEvent = Union[Message, Callback]
