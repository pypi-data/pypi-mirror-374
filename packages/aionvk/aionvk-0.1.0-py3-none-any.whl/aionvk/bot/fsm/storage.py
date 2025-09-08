import abc
from typing import Any, Dict, Optional


class BaseStorage(abc.ABC):
    """
    Абстрактный базовый класс для хранилищ состояний FSM.

    Определяет интерфейс, которому должны следовать все реализации
    хранилищ (например, RedisStorage, MemoryStorage).
    """

    @abc.abstractmethod
    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Получает данные состояния по ключу.

        :param key: Уникальный ключ (например, 'fsm:user_id:peer_id').
        :return: Словарь с данными состояния или None, если состояние не найдено.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def set_state(self, key: str, state_data: Dict[str, Any]) -> None:
        """
        Устанавливает или обновляет данные состояния по ключу.

        :param key: Уникальный ключ.
        :param state_data: Словарь с данными состояния (включая 'state' и 'data').
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def clear_state(self, key: str) -> None:
        """
        Удаляет данные состояния по ключу.

        :param key: Уникальный ключ.
        """
        raise NotImplementedError
