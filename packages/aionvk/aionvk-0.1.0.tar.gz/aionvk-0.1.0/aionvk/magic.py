from typing import Any, Callable, Iterable, Optional, Self

from .bot.filters import BaseFilter
from .types import VKEvent


class _NotSet:
    def __repr__(self) -> str:
        return "<Value is NOT SET>"


NOT_SET = _NotSet()


def _resolve_value(obj: Any, keys: tuple[str, ...]) -> Any:
    if not keys:
        return obj
    value = obj
    for key in keys:
        try:
            if isinstance(value, dict):
                value = value[key]
            else:
                value = getattr(value, key)
        except (KeyError, AttributeError, TypeError):
            return NOT_SET
    return value


class MagicFilter(BaseFilter):

    def __init__(
        self,
        key: tuple[str, ...] = (),
        logic: Optional[Callable[[Any], bool]] = None,
    ):
        self._key = key
        self._logic = logic

    async def check(self, event: VKEvent, **data: Any) -> bool:
        """
        Метод проверки, который делает MagicFilter настоящим фильтром.
        """
        if self._logic is None:
            # Если логики нет (например, просто F.text), проверяем на существование
            return _resolve_value(event, self._key) is not NOT_SET

        resolved_value = _resolve_value(event, self._key)
        if resolved_value is NOT_SET:
            return False
        return self._logic(resolved_value)

    def __getattr__(self, name: str) -> Self:
        return self.__class__(key=self._key + (name,))

    def __getitem__(self, name: str) -> Self:
        return self.__getattr__(name)

    def __eq__(self, value: Any) -> Self:
        return self.__class__(key=self._key, logic=lambda v: v == value)

    def __ne__(self, value: Any) -> Self:
        return self.__class__(key=self._key, logic=lambda v: v != value)

    def __gt__(self, value: Any) -> Self:
        return self.__class__(key=self._key, logic=lambda v: v > value)

    def __lt__(self, value: Any) -> Self:
        return self.__class__(key=self._key, logic=lambda v: v < value)

    def __ge__(self, value: Any) -> Self:
        return self.__class__(key=self._key, logic=lambda v: v >= value)

    def __le__(self, value: Any) -> Self:
        return self.__class__(key=self._key, logic=lambda v: v <= value)

    def contains(self, value: Any) -> Self:
        return self.__class__(
            key=self._key, logic=lambda v: isinstance(v, Iterable) and value in v
        )

    def is_in(self, container: Iterable[Any]) -> Self:
        return self.__class__(key=self._key, logic=lambda v: v in container)

    def is_(self, value: Any) -> Self:
        return self.__class__(key=self._key, logic=lambda v: v is value)

    def is_not(self, value: Any) -> Self:
        return self.__class__(key=self._key, logic=lambda v: v is not value)

    def startswith(self, value: str) -> Self:
        return self.__class__(
            key=self._key, logic=lambda v: isinstance(v, str) and v.startswith(value)
        )

    def endswith(self, value: str) -> Self:
        return self.__class__(
            key=self._key, logic=lambda v: isinstance(v, str) and v.endswith(value)
        )

    def exists(self) -> Self:
        return self.__class__(key=self._key)


F = MagicFilter()
