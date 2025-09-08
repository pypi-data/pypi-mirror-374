import abc
from typing import Any, Awaitable, Callable, Dict, List, Union

from ..types import Message, VKEvent
from .fsm.context import FSMContext


class BaseFilter(abc.ABC):
    """
    Базовый абстрактный фильтр.
    Используется как родитель для всех фильтров.
    """

    @abc.abstractmethod
    async def check(self, event: VKEvent, **data: Any) -> bool:
        """
        Проверяет событие.

        Args:
            event: Объект события (Message или Callback).
            data: Доп. данные (например, state).

        Returns:
            True если фильтр пройден, иначе False.
        """
        raise NotImplementedError

    def __and__(self, other: "BaseFilter") -> "AndFilter":
        """Комбинация фильтров через `&` (логическое И)."""
        return AndFilter(self, other)

    def __or__(self, other: "BaseFilter") -> "OrFilter":
        """Комбинация фильтров через `|` (логическое ИЛИ)."""
        return OrFilter(self, other)


class AndFilter(BaseFilter):
    """
    Фильтр-объединение (И).
    Проходит только если все вложенные фильтры вернули True.
    """

    def __init__(self, *filters: BaseFilter):
        self.filters = filters

    async def check(self, event: VKEvent, **data: Any) -> bool:
        return all([await f.check(event, **data) for f in self.filters])


class OrFilter(BaseFilter):
    """
    Фильтр-объединение (ИЛИ).
    Проходит если хотя бы один вложенный фильтр вернул True.
    """

    def __init__(self, *filters: BaseFilter):
        self.filters = filters

    async def check(self, event: VKEvent, **data: Any) -> bool:
        return any([await f.check(event, **data) for f in self.filters])


class TextFilter(BaseFilter):
    """
    Фильтр по тексту сообщения.

    Args:
        text: Строка или список строк для поиска.
        ignore_case: Игнорировать регистр (по умолчанию True).
    """

    def __init__(self, text: Union[str, List[str]], ignore_case: bool = True):
        self.texts = [text] if isinstance(text, str) else text
        self.ignore_case = ignore_case

    async def check(self, event: VKEvent, **data: Any) -> bool:
        if not isinstance(event, Message):
            return False

        text_to_check = event.text.lower() if self.ignore_case else event.text
        texts_to_find = (
            [t.lower() for t in self.texts] if self.ignore_case else self.texts
        )
        return text_to_check in texts_to_find


class CommandFilter(BaseFilter):
    """
    Фильтр по командам (например, `/start`).

    Args:
        commands: Строка или список команд.
        prefix: Префикс команд (по умолчанию "/").
    """

    def __init__(self, commands: Union[str, List[str]], prefix: str = "/"):
        cmds = [commands] if isinstance(commands, str) else commands
        self.commands = [cmd.lower() for cmd in cmds]
        self.prefix = prefix

    async def check(self, event: VKEvent, **data: Any) -> bool:
        if not isinstance(event, Message):
            return False
        text = event.text.lower().strip()
        return any(
            [text == cmd or text == f"{self.prefix}{cmd}" for cmd in self.commands]
        )


class StateFilter(BaseFilter):
    """
    Фильтр по состоянию FSM.

    Args:
        state: Объект состояния или строка (например, "MyStates.state1").
               Специальное значение `"*"` — любое состояние кроме None.
    """

    def __init__(self, state: Any):
        self.target_state = state.state if hasattr(state, "state") else state

    async def check(self, event: VKEvent, **data: Any) -> bool:
        fsm_context: FSMContext = data.get("state")

        if not fsm_context:
            return self.target_state is None

        current_state = await fsm_context.get_state()
        if self.target_state == "*":
            return current_state is not None

        return current_state == self.target_state


class PayloadFilter(BaseFilter):
    """
    Фильтр по payload у сообщений или callback-кнопок.

    Args:
        payload: Словарь, который должен входить в payload события.
    """

    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload

    async def check(self, event: VKEvent, **data: Any) -> bool:
        if not event.payload:
            return False
        return self.payload.items() <= event.payload.items()


class LambdaFilter(BaseFilter):
    """
    Фильтр, принимающий асинхронную функцию проверки.

    Args:
        func: Функция вида (event, data) -> bool.
    """

    def __init__(self, func: Callable[[VKEvent, Dict[str, Any]], Awaitable[bool]]):
        self.func = func

    async def check(self, event: VKEvent, **data: Any) -> bool:
        return await self.func(event, **data)
