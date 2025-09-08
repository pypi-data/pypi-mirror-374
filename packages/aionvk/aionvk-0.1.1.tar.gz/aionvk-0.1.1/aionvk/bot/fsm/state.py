from typing import Optional


class State:
    """Представляет одно конкретное состояние в группе."""

    def __init__(self, name: Optional[str] = None):
        self._name = name

    @property
    def state(self) -> str:
        """Возвращает полное имя состояния (например, 'MyStates:state1')."""
        if self._name is None:
            # Это исключение не должно возникать при правильном использовании StatesGroup
            raise RuntimeError("Имя состояния не было установлено через StatesGroup.")
        return self._name


class StatesGroup:
    """
    Базовый класс для группировки состояний.

    Использует метапрограммирование для автоматического присвоения
    полных имен дочерним состояниям во время определения класса.

    Пример:
    class MyStates(StatesGroup):
        state1 = State()
        state2 = State()

    assert MyStates.state1.state == "MyStates:state1"
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr, value in cls.__dict__.items():
            if isinstance(value, State):
                value._name = f"{cls.__name__}:{attr}"
