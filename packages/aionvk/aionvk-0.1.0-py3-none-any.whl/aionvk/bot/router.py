from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Union, Optional

from .filters import (
    AndFilter,
    BaseFilter,
    CommandFilter,
    PayloadFilter,
    StateFilter,
    TextFilter,
)


@dataclass
class Handler:
    callback: Callable[..., Any]
    filters: List[BaseFilter] = field(default_factory=list)


class Router:
    def __init__(self):
        self.handlers: List[Handler] = []

    def message(
        self,
        *custom_filters: BaseFilter,
        text: Union[str, List[str], None] = None,
        command: Union[str, List[str], None] = None,
        state: Any = None,
        payload: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Callable:
        filters = list(custom_filters)
        if text is not None:
            ignore_case = kwargs.get("ignore_case", True)
            filters.append(TextFilter(text, ignore_case=ignore_case))
        if command is not None:
            prefix = kwargs.get("prefix", "/")
            filters.append(CommandFilter(command, prefix=prefix))
        if state is not None:
            filters.append(StateFilter(state))
        if payload is not None:
            filters.append(PayloadFilter(payload))

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            handler = Handler(callback=callback, filters=[AndFilter(*filters)])
            self.handlers.append(handler)
            return callback

        return decorator

    def callback(
        self,
        *custom_filters: BaseFilter,
        state: Any = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Callable:
        filters = list(custom_filters)
        if state is not None:
            filters.append(StateFilter(state))
        if payload is not None:
            filters.append(PayloadFilter(payload))

        def decorator(callback: Callable[..., Any]) -> Callable[..., Any]:
            handler = Handler(callback=callback, filters=[AndFilter(*filters)])
            self.handlers.append(handler)
            return callback

        return decorator
