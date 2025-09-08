from typing import Any, Dict, Optional

from .state import State
from .storage import BaseStorage


class FSMContext:
    """
    Контекст состояния, предоставляющий API для управления FSM.
    """

    def __init__(self, storage: BaseStorage, user_id: int, peer_id: int):
        self.storage = storage
        self._key = f"fsm:{user_id}:{peer_id}"

    async def get_state(self) -> Optional[str]:
        """
        Получает текущее состояние пользователя.
        :return: str — имя состояния или None, если состояние не установлено.
        """
        data = await self.storage.get_state(self._key)
        return data.get("state") if data else None

    async def set_state(
        self, state: Optional[State], data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Устанавливает новое состояние.
        Если state=None → полностью сбрасывает состояние.
        Если data не передано → сохраняются существующие данные.
        Если data передано → заменяются все данные.

        :param state: Объект State или None для сброса состояния.
        :param data: Новый словарь данных или None.
        """
        if state is None:
            await self.clear()
            return

        # Если новые данные не заданы — берём старые
        if data is None:
            current_data = await self.get_data()
        else:
            current_data = data

        state_data = {"state": state.state, "data": current_data}
        await self.storage.set_state(self._key, state_data)

    async def get_data(self) -> Dict[str, Any]:
        """
        Получает данные, связанные с текущим состоянием.
        :return: dict — данные состояния (или пустой словарь).
        """
        data = await self.storage.get_state(self._key)
        return data.get("data", {}) if data else {}

    async def update_data(self, **kwargs: Any) -> None:
        """
        Обновляет данные в текущем состоянии без смены самого состояния.
        :param kwargs: пары ключ=значение для добавления/обновления.
        """
        current_storage_data = await self.storage.get_state(self._key) or {}

        # Создаём "data", если её ещё нет
        if "data" not in current_storage_data:
            current_storage_data["data"] = {}

        current_storage_data["data"].update(kwargs)

        await self.storage.set_state(self._key, current_storage_data)

    async def clear(self) -> None:
        """
        Полностью очищает состояние и данные.
        """
        await self.storage.clear_state(self._key)
