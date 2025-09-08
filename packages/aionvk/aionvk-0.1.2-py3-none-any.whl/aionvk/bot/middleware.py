import abc
from typing import Any, Awaitable, Callable, Dict

from ..types import VKEvent


class BaseMiddleware(abc.ABC):
    """Абстрактный базовый класс для middleware."""

    @abc.abstractmethod
    async def __call__(
        self,
        handler: Callable[[VKEvent, Dict[str, Any]], Awaitable[Any]],
        event: VKEvent,
        data: Dict[str, Any],
    ) -> Any:
        """
        Основной метод middleware.

        :param handler: Следующий middleware в цепочке или сам обработчик события.
        :param event: Объект события (Message или Callback).
        :param data: Словарь с дополнительными данными.
        :return: Результат выполнения следующего обработчика в цепочке.
        """
        raise NotImplementedError
